from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from pathlib import Path
from ..models import ForcingResponse, Forcing, RegisterRequest
from ..database import get_session

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
    