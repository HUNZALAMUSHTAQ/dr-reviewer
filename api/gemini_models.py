
from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class DifficultyLevel(Enum):
    BASIC = 1
    BEGINNER = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5
    SENIOR = 6
    PRINCIPAL = 7
    ARCHITECT = 8
    DISTINGUISHED = 9
    FELLOW = 10

class QuestionCategory(Enum):
    ARCHITECTURE = 'Architecture'
    SCALABILITY = 'Scalability'
    SECURITY = 'Security'
    PERFORMANCE = 'Performance'
    DESIGN_PATTERNS = 'Design Patterns'
    DATA_FLOW = 'Data Flow'
    INTEGRATION = 'Integration'
    DEPLOYMENT = 'Deployment'

class Question(BaseModel):
    question: str = Field(..., description="The technical design review question")
    difficulty: int = Field(..., ge=1, le=10, description="Difficulty level from 1 (basic) to 10 (expert level)")
    category: QuestionCategory = Field(..., description="The category of the question")

class QuestionsResponse(BaseModel):
    Questions: List[Question] = Field(..., description="List of technical design review questions")
