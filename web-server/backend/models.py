from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Vote(BaseModel):
    name: str
    vote: str

class Question(BaseModel):
    title: str
    description: str
    options: List[str]

class QuestionResponse(BaseModel):
    id: int
    title: str
    description: str
    options: List[str]
    active: bool

class User(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Session(BaseModel):
    user_id: int
    session_token: str