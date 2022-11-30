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
    screenshots: List[str] = None


class DefaultResponse(BaseModel):
    status: Optional[str]
    msg: Optional[str]


class DefaultResponseComment(DefaultResponse):
    results: List[str] = None


class Responses(BaseModel):
    results: List[DefaultResponse]
    
    
class ResponsesComment(BaseModel):
    results: List[DefaultResponseComment]
