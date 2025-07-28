import io
import json
from enum import Enum
from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

import pathlib

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

def parse_and_display_questions(response_text: str) -> List[Question]:
    """Parse JSON response and display questions in a readable format using Pydantic models"""
    try:
        # Parse using Pydantic model
        questions_response = QuestionsResponse.model_validate_json(response_text)
        questions = questions_response.Questions
        
        print("Parsed Questions:")
        for i, q in enumerate(questions, 1):
            # Get difficulty level description
            try:
                difficulty_desc = DifficultyLevel(q.difficulty).name
            except ValueError:
                difficulty_desc = "UNKNOWN"
            
            print(f"{i}. {q.question}")
            print(f"   Category: {q.category.value}")
            print(f"   Difficulty: {q.difficulty}/10 ({difficulty_desc})")
            print()
        return questions
    except Exception as e:
        print(f"Error parsing response with Pydantic: {e}")
        print("Raw response:", response_text)
        return []

client = genai.Client(
  api_key="AIzaSyCVSszBw1kuA1MhqxxpeSA1_11iGR2h5d8",
)

prob = pathlib.Path('./prob.pdf')
mlp = pathlib.Path('./mlp.pdf')

sample_pdf_1 = types.Part.from_bytes(
        data=prob.read_bytes(),
        mime_type='application/pdf',
      )

sample_pdf_2 = types.Part.from_bytes(
        data=mlp.read_bytes(),
        mime_type='application/pdf',
      )

# Create initial user message with PDFs as history
user_message_with_pdfs = types.Content(
    role="user",
    parts=[
        types.Part(text="Please analyze these two PDF documents. My name is Hunzala Mushtaq and I'm 20 years old."),
        sample_pdf_1,
        sample_pdf_2
    ]
)
instruction = """You are a seasoned Software Architect responsible for conducting Design Reviews. Your audience is typically technical leads or senior developers presenting their architectural design for a new system, feature, or service.

For each design case presented, your goal is to:
- Understand the architecture: Clarify the system’s components, responsibilities, and interactions.
- Ask probing, relevant questions based on best practices, patterns, and potential trade-offs.
- Identify architectural gaps, risks, or anti-patterns in scalability, maintainability, security, data flow, fault tolerance, and integration.
- Ensure alignment with principles like SOLID, Domain-Driven Design, cloud-native architecture, and modularity (where applicable).
- Always ask questions specific to the design presented, such as:
- What are the key components/modules and their responsibilities?
- How does the system handle failures or retries?
- What data consistency strategy is in place (eventual vs. strong)?
- How is versioning, logging, or monitoring handled?
- Are there any third-party dependencies, and how are they abstracted?
- What are the scaling and deployment strategies (e.g., containers, serverless, microservices)?
- How is security handled (e.g., authN/authZ, data at rest/in transit)?
- What trade-offs were considered in selecting this architecture?


Ask at least 5 questions and then also ask the follow-up questions after the response of the user. """
system_instruction = types.Content(
    role="system",
    parts=[types.Part(text=instruction)]
)

# Create a simple model response to complete the conversation pair
model_response = types.Content(
    role="model",
    parts=[types.Part(text="I have received and analyzed both PDF documents. I can see that your name is Hunzala Mushtaq and you are 20 years old. I'm ready to answer any questions about the documents.")]
)

# Create generation config with structured output using Pydantic models
generation_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=QuestionsResponse,  # Use Pydantic model directly
    system_instruction=system_instruction
)

# Create chat session with PDFs in history and structured output config
chat = client.chats.create(
    model="gemini-2.0-flash-001",
    history=[user_message_with_pdfs, model_response],
    config=generation_config
)

print("=== Chat created with PDFs in history and structured output ===")
print("Ready to ask questions about the documents...")
print("\n" + "="*50 + "\n")

# First follow-up message - Generate questions about the documents
print("=== Generating structured questions from PDFs ===")
response = chat.send_message("Based on the PDF documents provided, generate 5 technical design review questions. Each question should have a difficulty rating from 1-10 (1 being basic, 10 being expert level) and a category from: Architecture, Scalability, Security, Performance, Design Patterns, Data Flow, Integration, or Deployment. Focus on architecture, scalability, security, and best practices.")
print("Raw JSON response:")
print(response.text)
print("\n" + "-"*30 + "\n")
parse_and_display_questions(response.text)
print("\n" + "="*50 + "\n")

# # Second follow-up message - More specific questions
# print("=== Generating questions about specific design patterns ===")
# response = chat.send_message("Generate 3 questions specifically about design patterns, SOLID principles, and architectural trade-offs mentioned in the documents. Rate their difficulty from 1-10 and assign appropriate categories.")
# print("Raw JSON response:")
# print(response.text)
# print("\n" + "-"*30 + "\n")
# parse_and_display_questions(response.text)
# print("\n" + "="*50 + "\n")

# # Third follow-up message - Security focused questions
# print("=== Generating security-focused questions ===")
# response = chat.send_message("Create 4 questions focused on security, authentication, authorization, and data protection aspects from the documents. Include difficulty ratings 1-10 and assign Security category.")
# print("Raw JSON response:")
# print(response.text)
# print("\n" + "-"*30 + "\n")
# parse_and_display_questions(response.text)
# print("\n" + "="*50 + "\n")

# Validation example
print("=== Pydantic Model Validation Example ===")
try:
    # Create a sample question programmatically
    sample_question = Question(
        question="How does the system handle distributed transactions?",
        difficulty=8,
        category=QuestionCategory.ARCHITECTURE
    )
    print("Valid question created:")
    print(f"Question: {sample_question.question}")
    print(f"Category: {sample_question.category.value}")
    print(f"Difficulty: {sample_question.difficulty}")
    
    # Create response object
    sample_response = QuestionsResponse(Questions=[sample_question])
    print(f"\nJSON output: {sample_response.model_dump_json(indent=2)}")
    
except Exception as e:
    print(f"Validation error: {e}")
print("\n" + "="*50 + "\n")