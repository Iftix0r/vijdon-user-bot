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
    username = Column(String, nullable=True)
    message_text = Column(String)
    is_passenger = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)
    extracted_data = Column(String)
    source_chat_id = Column(String, nullable=True)
    accepted = Column(Boolean, default=False)
    rejected = Column(Boolean, default=False)

class Blacklist(Base):
    __tablename__ = 'blacklist'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True)
    reason = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///bot_data.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
