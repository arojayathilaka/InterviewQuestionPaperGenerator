from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QuestionItem(BaseModel):
    """Represents a single question in the paper"""
    id: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    difficulty_level: str  # "Easy", "Medium", "Hard"
    topic: str
    explanation: Optional[str] = None


class PaperGenerationRequest(BaseModel):
    """Request model for generating a question paper"""
    user_id: str
    technology_topic: str
    num_questions: int = Field(default=10, ge=1, le=100)
    difficulty_level: str = Field(default="mixed", pattern="^(easy|medium|hard|mixed)$")
    question_types: List[str] = Field(default=["multiple_choice"], min_items=1)
    duration_minutes: int = Field(default=60, ge=15, le=180)
    preferences: Optional[str] = None


class PaperGenerationResponse(BaseModel):
    """Response model for generated question paper"""
    paper_id: str
    user_id: str
    technology_topic: str
    created_at: datetime
    questions: List[QuestionItem]
    total_questions: int
    difficulty_distribution: dict  # e.g., {"easy": 3, "medium": 5, "hard": 2}
    paper_url: str  # URL in blob storage
    status: str  # "completed", "failed"


class UserProfile(BaseModel):
    """User profile model"""
    user_id: str
    email: str
    name: str
    created_at: datetime
    papers_generated: int = 0
    preferences: Optional[dict] = None
