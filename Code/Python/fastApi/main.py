from typing import Annotated
from datetime import datetime

from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel, Field

app = FastAPI()

task_db = {}

class Task(BaseModel):
    task : str
    description: str | None = None
    updated: str  = Field(default_factory=lambda:datetime.now().isoformat())
    completed: bool = Field(default=False)
    
@app.post("/Task/")
async def createtask(task: Task):
    task_id = len(task_db) + 1
    task_db[task_id] = {"task_id": task_id, **task.dict()}
    return task_db[task_id]

@app.get("/Task/")
async def get_task():
    return list(task_db.values())

@app.get("/Task/{task_id}")
async def list_task_id(task_id: int):
    if task_id in task_db:
        return task_db.get(task_id, {"message":"Task Not Found"})
    return {"message": "Task Not Found"}

@app.put("/Task/{task_id}")
async def update_todo(task_id: int, task: Task):
    if task_id in task_db:
        task_db[task_id] = {"task_id": task_id, **task.dict()}
        return task_db[task_id]
    return {"message": "Task not found"}

@app.delete("/Task/{task_id}")
async def del_task(task_id: int):
    if task_id in task_db:
        del task_db[task_id]
        return {"message": "Task deleted"}
    return {"message": "Task not found"}
