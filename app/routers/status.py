from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from ..models import Status

router = APIRouter(prefix="/forcing", tags=['status'])

def check_slurm_status(slurm_job_id: str) -> Status:
    returncode, stdout, _ = run_remote()