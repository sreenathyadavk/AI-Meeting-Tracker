"""
Database models and session management
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Meeting(Base):
    """Meeting record with metadata"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    transcript = Column(Text, nullable=False)
    transcript_length = Column(Integer, nullable=False)
    status = Column(String, default="completed")  # processing, completed, failed
    
    # Relationships
    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="meeting", cascade="all, delete-orphan")


class Task(Base):
    """Extracted task/action item"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    task = Column(Text, nullable=False)
    owner = Column(String, default="unknown")
    deadline = Column(String, default="unknown")
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    meeting = relationship("Meeting", back_populates="tasks")


class Chat(Base):
    """Chat messages about a meeting"""
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    meeting = relationship("Meeting", back_populates="chats")


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
