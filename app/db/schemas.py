from pydantic import BaseModel, Field
from typing import Optional, List


class BotSchema(BaseModel):
    login: Optional[str]
    password: Optional[str]
    
    class Config:
        orm_mode = True
        

class ActionSchemaBase(BaseModel):
    login: Optional[str] = None
    
    class Config:
        orm_mode = True
        
        
class ActionSchema(ActionSchemaBase):
    target_id: int
    
    
class ActionSchemaComment(ActionSchema):
    comment: str


class DefaultResponse(BaseModel):
    status: Optional[str]
    msg: Optional[str]


class Responses(BaseModel):
    results: List[DefaultResponse]

