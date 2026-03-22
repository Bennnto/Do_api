from typing import Annotated
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column,  Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

from fastapi import Body, FastAPI, Path, Query, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.authentication import AuthCredentials, SimpleUser
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, Field
import os

app = FastAPI()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
#ACCESS_TOKEN_EXPIRE_HOURS = 48

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

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

class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("TaskDB", back_populates="owner")

class TaskDB(Base):
    __tablename__ = "tasks"
     
    task_id = Column(Integer, primary_key=True, index=True)
    task = Column(String) 
    description = Column(String, nullable=True)
    updated = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default='Medium')
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # ADD THIS LINE
    
    owner = relationship("UserDB", back_populates="tasks") 
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally :
        db.close()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int

class Task(BaseModel):
    task: str
    description: str | None = None
    completed: bool = Field(default=False)
    due_date: str | None = None
    priority: str = Field(default='Medium')

class TaskResponse(Task):
    task_id: int
    updated: str

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str)-> bool :
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=48)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    user_id = verify_token(token)
    user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/users/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(UserDB).filter(
        (UserDB.username == user.username) | (UserDB.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = UserDB(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    created_at_str = db_user.created_at.isoformat() if db_user.created_at else datetime.utcnow().isoformat()
    return UserResponse(
        user_id=db_user.user_id,
        username=db_user.username,
        email=db_user.email,
        created_at=created_at_str
    )

@app.post("/users/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by username
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create JWT token
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally :
        db.close()    
    
@app.post("/Task/")
async def createtask(task: Task, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    task_data = task.dict()
    if task_data.get('due_date'):
        try:
            task_data['due_date'] = datetime.fromisoformat(task_data['due_date'])
        except (ValueError, TypeError):
            task_data['due_date'] = None
    
    db_task = TaskDB(**task_data, user_id=current_user.user_id)  # ADD user_id
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/Task/")
async def get_task(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(TaskDB).filter(TaskDB.user_id == current_user.user_id).all()
    
@app.get("/Task/{task_id}", response_model=TaskResponse)
async def list_task_id(task_id: int, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(TaskDB).filter(
        (TaskDB.task_id == task_id) & (TaskDB.user_id == current_user.user_id)
    ).first()
    if task:
        return task
    return {"message": "Task Not Found"}

    
@app.put("/Task/{task_id}", response_model=TaskResponse)
async def update_todo(task_id: int, task: Task, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(TaskDB).filter(
        (TaskDB.task_id == task_id) & (TaskDB.user_id == current_user.user_id)
    ).first()
    

@app.delete("/Task/{task_id}")
async def del_task(task_id: int, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(TaskDB).filter(
        (TaskDB.task_id == task_id) & (TaskDB.user_id == current_user.user_id)
    ).first()
