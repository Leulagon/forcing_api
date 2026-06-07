import subprocess
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from pathlib import Path
from ..models import ForcingResponse, Forcing, RegisterRequest, JobHandle, Status
from ..database import get_session
from ..config import get_settings

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


@router.post("{forcing_id}/mask", response_model=JobHandle)
def mask(forcing_id: int, session: Session = Depends(get_session)):
    forcing = session.get(Forcing, forcing_id)
    if forcing is None:
        raise HTTPException(status_code=404, detail=f"Forcing id {forcing_id} not found")
    
    grid_dir = Path(forcing.grid_dir)
    nc_files = list(grid_dir.rglob('*.nc'))
    if not nc_files:
        raise HTTPException(status_code=404, detail=f"No nc files in directory")
    
    mask_path = grid_dir / f"{forcing.name}_masK_latlon.tif"

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