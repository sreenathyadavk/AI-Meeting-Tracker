from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
import logging

# Import our modules
from modules.transcription import transcribe_audio
from modules.task_extractor import extract_tasks
from database import init_db, get_db, Meeting, Task, Chat
from config import settings

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AI Meeting Tracker",
    description="Self-hosted AI-powered meeting transcription and task extraction",
    version="1.0.0"
)

# CORS configuration from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "running",
        "service": "AI Meeting Tracker",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with database connectivity test"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "ollama_host": settings.ollama_host
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/api/upload")
async def upload_recording(file: UploadFile = File(...)):
    """
    Upload a meeting recording (MP3/MP4)
    Returns meeting_id and file info
    """
    try:
        # Validate file type
        allowed_extensions = [".mp3", ".mp4", ".wav", ".m4a"]
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded successfully: {file.filename}")
        
        return {
            "status": "success",
            "filename": file.filename,
            "path": str(file_path),
            "size": file_path.stat().st_size
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process")
async def process_recording(filename: str, db: Session = Depends(get_db)):
    """
    Process uploaded recording:
    1. Transcribe with Whisper
    2. Extract tasks with Ollama
    3. Store in database
    """
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"Starting transcription for: {filename}")
        
        # Step 1: Transcribe audio
        transcript = await transcribe_audio(str(file_path))
        logger.info(f"Transcription complete. Length: {len(transcript)} chars")
        
        # Step 2: Extract tasks using Ollama
        logger.info("Extracting tasks with Ollama...")
        tasks = await extract_tasks(transcript)
        logger.info(f"Extracted {len(tasks)} tasks")
        
        # Step 3: Store in database
        meeting = Meeting(
            filename=filename,
            transcript=transcript,
            transcript_length=len(transcript),
            status="completed"
        )
        db.add(meeting)
        db.flush()  # Get meeting ID
        
        # Add tasks
        for task_data in tasks:
            task = Task(
                meeting_id=meeting.id,
                task=task_data.get("task", ""),
                owner=task_data.get("owner", "unknown"),
                deadline=task_data.get("deadline", "unknown"),
                confidence=task_data.get("confidence", 0.5)
            )
            db.add(task)
        
        db.commit()
        db.refresh(meeting)
        
        # Return response
        return {
            "status": "success",
            "meeting_id": meeting.id,
            "filename": filename,
            "transcript": transcript,
            "tasks": tasks,
            "task_count": len(tasks)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings")
async def list_meetings(limit: int = 10, db: Session = Depends(get_db)):
    """Get list of recent meetings"""
    try:
        meetings = db.query(Meeting).order_by(Meeting.upload_date.desc()).limit(limit).all()
        
        result = []
        for meeting in meetings:
            result.append({
                "id": meeting.id,
                "filename": meeting.filename,
                "upload_date": meeting.upload_date.isoformat(),
                "task_count": len(meeting.tasks),
                "transcript_length": meeting.transcript_length
            })
        
        return {"meetings": result}
    except Exception as e:
        logger.error(f"Error listing meetings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings/{meeting_id}")
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Get meeting details by ID"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "id": meeting.id,
        "filename": meeting.filename,
        "upload_date": meeting.upload_date.isoformat(),
        "transcript": meeting.transcript,
        "tasks": [
            {
                "task": task.task,
                "owner": task.owner,
                "deadline": task.deadline,
                "confidence": task.confidence
            }
            for task in meeting.tasks
        ],
        "task_count": len(meeting.tasks)
    }

@app.post("/api/chat")
async def chat_about_meeting(question: str, transcript: str, meeting_id: int = None, db: Session = Depends(get_db)):
    """
    Answer questions about the meeting using Ollama
    
    Args:
        question: User's question about the meeting
        transcript: Meeting transcript for context
    
    Returns:
        AI-generated answer based on the transcript
    """
    try:
        import ollama
        
        logger.info(f"Chat question: {question}")
        
        prompt = f"""Based on this meeting transcript, answer the following question.

Transcript: {transcript}

Question: {question}

Provide a helpful, concise answer based only on the information in the transcript."""

        response = ollama.chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = response['message']['content']
        logger.info(f"Chat answer generated: {len(answer)} chars")
        
        # Store chat in database if meeting_id provided
        if meeting_id:
            chat = Chat(
                meeting_id=meeting_id,
                question=question,
                answer=answer
            )
            db.add(chat)
            db.commit()
        
        return {
            "status": "success",
            "question": question,
            "answer": answer
        }
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
