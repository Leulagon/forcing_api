from enum import Enum
from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

class Stage(str, Enum):
    mask = "mask"
    spweights = "spweights"
    remapping = "remapping"
    nh_reformat = "nh_reformat"
    train = "train"

class Status(str, Enum):
    waiting = "waiting"
    running = "running"
    failed = "failed"
    completed = "completed"

class Forcing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    grid_dir: str
    status: Status = Field(default=Status.waiting)
    prcp_var: Optional[str] = Field(default=None)
    tmin_var: Optional[str] = Field(default=None)
    tmax_var: Optional[str] = Field(default=None)

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    forcing_id: int = Field(foreign_key="forcing_id", index=True)
    stage: Stage
    slurm_job_id: str
    status: Status

#-------------------------
# SCHEMA
#-------------------------

class RegisterRequest(BaseModel):
    name: str
    grid_dir: str
    prcp_var: Optional[str] = None
    tmin_var: Optional[str] = None
    tmax_var: Optional[str] = None

class ForcingResponse(BaseModel):
    id: int
    name: str
    grid_dir: str

class JobHandle(BaseModel):
    forcing_id: int
    status: Status
    message: str = ""