from pydantic import BaseModel
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
