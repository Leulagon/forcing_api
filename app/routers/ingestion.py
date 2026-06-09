import subprocess
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from pathlib import Path
from ..models import ForcingResponse, Forcing, RegisterRequest, JobHandle, Status, Job, Stage
from ..database import get_session
from ..config import get_settings
from ..ssh import run_remote

router = APIRouter(prefix="/ingest", tags=['ingestion'])

def validate_grid_dir(grid_dir: str) -> None:
    path = Path(grid_dir)
    if not path.exists():
        raise HTTPException(status_code=400, detail="Directory does not exist")
    if not path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")

    nc_files = list(path.rglob("*.nc"))
    if not nc_files:
        raise HTTPException(status_code=400, detail="No .nc files found in directory")
    

@router.post("/register", response_model=ForcingResponse)
def register(req: RegisterRequest, session: Session = Depends(get_session)):
    validate_grid_dir(req.grid_dir)

    forcing=Forcing(
        name=req.name,
        grid_dir=req.grid_dir,
        prcp_var=req.prcp_var,
        tmax_var=req.tmax_var,
        tmin_var=req.tmin_var 
    )

    session.add(forcing)
    session.commit()
    session.refresh(forcing)
    return forcing


@router.post("/{forcing_id}/mask", response_model=JobHandle)
def mask(forcing_id: int, session: Session = Depends(get_session)):
    forcing = session.get(Forcing, forcing_id)
    if forcing is None:
        raise HTTPException(status_code=404, detail=f"Forcing id {forcing_id} not found")
    
    grid_dir = Path(forcing.grid_dir)
    nc_files = list(grid_dir.rglob('*.nc'))
    if not nc_files:
        raise HTTPException(status_code=404, detail=f"No nc files in directory")
    
    mask_path = grid_dir.parent / f"{forcing.name}_mask_latlon.tif"

    settings = get_settings()
    script = settings.scripts_dir / "make_latlon_mask.py"

    result = subprocess.run(
        ["python", str(script), str(nc_files[0]), str(mask_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"make_latlon_mask.py failed: {result.stderr.strip()}")
    
    return JobHandle(
        forcing_id=forcing_id,
        status=Status.completed,
        message=str(mask_path)
    )

@router.post("/{forcing_id}/spweights", response_model=JobHandle)
def spweights(forcing_id: int, session: Session = Depends(get_session)):
    forcing = session.get(Forcing, forcing_id)
    if forcing is None:
        raise HTTPException(status_code=400, detail=f"forcing id {forcing_id} not found")
    
    settings = get_settings()

    mask_path    = Path(forcing.grid_dir).parent / f"{forcing.name}_mask_latlon.tif"
    weights_path = settings.project_dir / "spweights" / f"spweights_{forcing.name}_to_CAMELS-GII.nc"
    job_script   = settings.project_dir / Path("wendian-job-scripts/spweights_job.sh")

    if not mask_path.exists():
        raise HTTPException(status_code=400, detail=f"Mask not found at {mask_path}. Run /mask first.")

    sbatch_cmd = f"GRID_NAME={mask_path} MAPPING_NC_NAME={weights_path} sbatch {job_script}"

    returncode, stdout, stderr = run_remote(sbatch_cmd)

    if returncode != 0:
        raise HTTPException(status_code=500, detail=f"sbatch failed. \n{stderr.strip()}")
    
    # sbatch will print "submitted batch job {ID}" to stdout, grabbing from that
    slurm_job_id = stdout.strip().split()[-1]

    job = Job(
        forcing_id=forcing_id,
        stage=Stage.spweights,
        slurm_job_id=slurm_job_id,
        status=Status.running
    )
    session.add(job)
    session.commit()

    return JobHandle(
        forcing_id=forcing_id,
        status=Status.running,
        message=f"SLURM job {slurm_job_id}"
    )


@router.post("/{forcing_id}/basin_remapping")
def basin_remapping(forcing_id: int, session: Session = Depends(get_session)):
    forcing = session.get(Forcing, forcing_id)
    if not forcing:
        raise HTTPException(status_code=400, detail="forcing id {forcing_id} not found")
    