from sqlmodel import SQLModel, create_engine, Session
from . import models

DB_URL = "sqlite:///./forcings.db"
engine = create_engine(DB_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session