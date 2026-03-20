from typing import Annotated
from datetime import datetime
from sqlalchemy import create_engine, Column,  Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from fastapi import Body, FastAPI, Path, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
#Data Base Setup
# DATABASE_URL = "postgresql://do_api_user:dlvIhVsQjW81PS0whqCMIveJIIXipCXg@dpg-d6u2emvdiees73d9ehog-a:5432/do_api"
DATABASE_URL = "sqlite:///./test.db"
# Note: SQLite needs connect_args={"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TaskDB(Base):
    __tablename__ = "tasks"
     
    task_id = Column(Integer, primary_key=True, index=True)
    task = Column(String) 
    description = Column(String, nullable=True)
    updated = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default='Medium')


Base.metadata.create_all(bind=engine)

class Task(BaseModel):
    task: str
    description: str | None = None
    completed: bool = Field(default=False)
    due_date: str | None = None
    priority: str = Field(default='Medium')

class TaskResponse(Task):
    task_id: int
    updated: str

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally :
        db.close()    
    
@app.post("/Task/")
async def createtask(task: Task, db: Session = Depends(get_db)):
    task_data = task.dict()
    if task_data.get('due_date'):
        try:
            task_data['due_date'] = datetime.fromisoformat(task_data['due_date'])
        except (ValueError, TypeError):
            task_data['due_date'] = None
            
    db_task = TaskDB(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/Task/")
async def get_task(db: Session = Depends(get_db)):
    return db.query(TaskDB).all()
    
@app.get("/Task/{task_id}", response_model=TaskResponse)
async def list_task_id(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if task:
        return task
    return {"message": "Task Not Found"}
    
@app.put("/Task/{task_id}", response_model=TaskResponse)
async def update_todo(task_id: int, task: Task, db: Session = Depends(get_db)):
    db_task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if db_task:
        task_data = task.dict()
        if task_data.get('due_date'):
            try:
                task_data['due_date'] = datetime.fromisoformat(task_data['due_date'])
            except (ValueError, TypeError):
                task_data['due_date'] = None
        for key, value in task_data.items():
            setattr(db_task, key, value)
        db_task.updated = datetime.now()
        db.commit()
        db.refresh(db_task)
        return db_task
    return {"message": "Task not found"}

@app.delete("/Task/{task_id}")
async def del_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return {"message": "Task deleted"}
    return {"message": "Task not found"}

