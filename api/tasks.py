from celery import shared_task
import time
import pathlib
from .models import DesignDocument, ProbingQuestions
from google import genai
from google.genai import types
from django.core.files.storage import default_storage
from .models import DesignReview

from typing import List
from .gemini_models import Question, QuestionsResponse  # Make sure these are imported correctly

def parse_questions(response_text: str) -> List[Question]:
    """
    Parse Gemini JSON response using Pydantic models.
    Returns a list of validated `Question` objects.
    """
    try:
        questions_response = QuestionsResponse.model_validate_json(response_text)
        return questions_response.Questions
    except Exception as e:
        raise ValueError(f"Parsing failed: {e}")


@shared_task
def example_task():
    """
    Example Celery task that simulates some work
    """
    time.sleep(5)  # Simulate some work
    return "Task completed successfully"


@shared_task
def process_document_task(document_id):
    """
    Example task for processing documents
    """
    # Simulate document processing
    time.sleep(3)
    return f"Document {document_id} processed successfully"


@shared_task
def generate_questions_task(document_id):
    """
    Example task for generating questions from documents
    """
    # Simulate question generation
    time.sleep(10)
    return f"Questions generated for document {document_id}" 


@shared_task
def generate_probing_questions_for_review(design_review_id):
    

    try:
        review = DesignReview.objects.get(id=design_review_id)
        docs = review.documents.all()
        print(docs)
        # Load PDF files
        parts = []
        for doc in docs:
            local_path = default_storage.path(doc.path)
            pdf_part = types.Part.from_bytes(
                data=pathlib.Path(local_path).read_bytes(),
                mime_type='application/pdf'
            )
            parts.append(pdf_part)

        # Gemini Setup
        client = genai.Client(api_key="AIzaSyCVSszBw1kuA1MhqxxpeSA1_11iGR2h5d8")

        user_message = types.Content(
            role="user",
            parts=[types.Part(text=f"Analyze the documents for design review {review.id}.")] + parts
        )

        system_instruction = types.Content(
            role="system",
            parts=[types.Part(text="""You are a seasoned Software Architect... (your prompt here)""")]
        )

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QuestionsResponse,
            system_instruction=system_instruction
        )

        chat = client.chats.create(
            model="gemini-2.0-flash-001",
            history=[user_message],
            config=config
        )

        response = chat.send_message(
            "Generate 5 technical design review questions with difficulty rating (1-10) and category."
        )

        parsed_questions = parse_questions(response.text)
        print(parsed_questions)
        # Save to DB
        for pq in parsed_questions:
            ProbingQuestions.objects.create(
                designReview=review,
                question=pq.question,
                difficulty=pq.difficulty
            )

        return f"Generated {len(parsed_questions)} questions for DesignReview ID {review.id}"

    except Exception as e:
        return f"Failed to generate questions for review {design_review_id}: {str(e)}"
