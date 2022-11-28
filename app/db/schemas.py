from pydantic import BaseModel, Field
from typing import Optional, List


class BotSchema(BaseModel):
    login: Optional[str]
    password: Optional[str]
    
    class Config:
        orm_mode = True
        

class ActionSchema(BaseModel):
    login: Optional[str] = None
    target_id: Optional[int] = None
    comment: Optional[str] = None
    
    class Config:
        orm_mode = True
    

class DefaultResponse(BaseModel):
    login: str = None
    status: Optional[str]
    msg: Optional[str]
    

class Responses(BaseModel):
    results: List[DefaultResponse]