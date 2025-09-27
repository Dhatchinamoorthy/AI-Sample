from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.chat import ChatSession, Message
from app.services.llm_service import LLMService

router = APIRouter()

# Pydantic models for request/response
class ChatSessionCreate(BaseModel):
    user_id: str
    title: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: int
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str
    role: str = "user"

class MessageResponse(BaseModel):
    id: int
    session_id: int
    content: str
    role: str
    widgets: Optional[List[dict]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    session_id: int
    widgets: Optional[List[dict]] = None


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    db_session = ChatSession(
        user_id=session_data.user_id,
        title=session_data.title
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return session


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get all messages for a chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    
    return messages


@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message and get AI response with widgets"""
    try:
        # Get or create session
        if chat_request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == chat_request.session_id
            ).first()
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found"
                )
        else:
            # Create new session
            session = ChatSession(
                user_id=chat_request.user_id,
                title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # Save user message
        user_message = Message(
            session_id=session.id,
            content=chat_request.message,
            role="user"
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        # Get AI response with widgets
        llm_service = LLMService()
        ai_response = await llm_service.process_message(chat_request.message)
        
        # Save AI response
        ai_message = Message(
            session_id=session.id,
            content=ai_response.get("content", ""),
            role="assistant",
            widgets=ai_response.get("widgets", [])
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        return ChatResponse(
            user_message=user_message,
            assistant_message=ai_message,
            session_id=session.id,
            widgets=ai_response.get("widgets", [])
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_sessions(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a user"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return sessions


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}
