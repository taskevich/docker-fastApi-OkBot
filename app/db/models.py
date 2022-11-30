from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from ..core.config import Base
    

class Events(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    target_id = Column(String)
    type_action = Column(String)
    date_event = Column(DateTime(timezone=True), server_default=func.now())
    
    
class Accounts(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)