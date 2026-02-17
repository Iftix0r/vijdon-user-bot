from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class SourceGroup(Base):
    __tablename__ = 'source_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, unique=True)
    name = Column(String, nullable=True)
    active = Column(Boolean, default=True)

class Log(Base):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)
    message_text = Column(String)
    is_passenger = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)
    extracted_data = Column(String) # JSON string

engine = create_engine('sqlite:///bot_data.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
