from celery import shared_task
import time
import pathlib
from .models import DesignDocument, ProbingQuestions
from google import genai
from google.genai import types
from django.core.files.storage import default_storage
from .models import DesignReview

from typing import List
from .gemini_models import Question, QuestionsResponse, EvaluationResponse  # Make sure these are imported correctly

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


def parse_evaluation(response_text: str) -> EvaluationResponse:
    """
    Parse Gemini JSON evaluation response using Pydantic models.
    Returns a validated `EvaluationResponse` object.
    """
    try:
        evaluation_response = EvaluationResponse.model_validate_json(response_text)
        return evaluation_response
    except Exception as e:
        raise ValueError(f"Evaluation parsing failed: {e}")


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
        
        candidate_response = GENERATE_CANDIDATE_RESPONSE_PROMPT(review)
        print(candidate_response)
        # Gemini Setup
        client = genai.Client(api_key="AIzaSyCVSszBw1kuA1MhqxxpeSA1_11iGR2h5d8")

        user_message = types.Content(
            role="user",
            parts=[types.Part(text=f"Analyze the documents for design review {review.id}.")] + parts
        )

        system_prompt_text = f"""You are a seasoned Software Architect responsible for conducting Design Reviews. Your audience is typically technical leads or senior developers presenting their architectural design for a new system, feature, or service.
For each design case presented, your goal is to:
- Understand the architecture: Clarify the system's components, responsibilities, and interactions.
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

Based on the candidate's approach described above, generate targeted questions that will help evaluate their design decisions and uncover potential issues or improvements. Ask at least 5 questions with varying difficulty levels.

The candidate's approach to the design review to above document is as follows review the approach according to the Document provided:
{candidate_response}

"""

        system_instruction = types.Content(
            role="system",
            parts=[types.Part(text=system_prompt_text)]
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
            "Generate 5 to 10 technical design review questions according to the Document provided and with difficulty rating (1-10) and category."
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

        # Update DesignReview status to "Questions Generated"
        
        review.status = 'Questions Generated'
        review.save()

        # Update all DesignDocument status to "analyzed"
        docs.update(isProcessed='analyzed')

        return f"Generated {len(parsed_questions)} questions for DesignReview ID {review.id}"

    except Exception as e:
        return f"Failed to generate questions for review {design_review_id}: {str(e)}"

def GENERATE_CANDIDATE_RESPONSE_PROMPT(design_review: DesignReview):
    def safe_get(value):
        return value if value else "USER does not provide any answer"

    instruction = (
        "THIS IS THE CANDIDATE WAY OF APPROACHING THE PROBLEM:\n\n"
        f"Problem Description:\n{safe_get(design_review.problemDescription)}\n\n"
        f"Proposed Architecture:\n{safe_get(design_review.proposedArchitecture)}\n\n"
        f"Design Tradeoffs:\n{safe_get(design_review.designTradeoffs)}\n\n"
        f"Scalability:\n{safe_get(design_review.scalibilty)}\n\n"
        f"Security Measures:\n{safe_get(design_review.securityMeasures)}\n\n"
        f"Maintainability:\n{safe_get(design_review.maintainability)}"
    )
    return instruction


@shared_task
def evaluate_design_review_task(design_review_id):
    """
    Evaluate a design review based on documents, questions, and answers.
    Creates a comprehensive evaluation score and feedback.
    """
    try:
        # 1. Get the design review and candidate information
        review = DesignReview.objects.get(id=design_review_id)
        candidate = review.candidate
        
        # 2. Get all design review information
        design_info = {
            "problemDescription": review.problemDescription or "Not provided",
            "proposedArchitecture": review.proposedArchitecture or "Not provided", 
            "designTradeoffs": review.designTradeoffs or "Not provided",
            "scalability": review.scalibilty or "Not provided",
            "securityMeasures": review.securityMeasures or "Not provided",
            "maintainability": review.maintainability or "Not provided"
        }
        
        # 3. Get all design documents
        documents = review.documents.all()
        
        # 4. Get all probing questions and answers
        probing_questions = review.probing_questions.all()
        
        # Format questions and answers in readable form
        qa_pairs = []
        for i, pq in enumerate(probing_questions, 1):
            qa_pairs.append(f"Question {i}: {pq.question}")
            qa_pairs.append(f"Answer {i}: {pq.answer or 'No answer provided'}")
            qa_pairs.append("")  # Empty line for readability
        
        qa_text = "\n".join(qa_pairs)
        
        # Prepare document parts for Gemini
        parts = []
        for doc in documents:
            try:
                local_path = default_storage.path(doc.path)
                pdf_part = types.Part.from_bytes(
                    data=pathlib.Path(local_path).read_bytes(),
                    mime_type='application/pdf'
                )
                parts.append(pdf_part)
            except Exception as e:
                print(f"Could not load document {doc.path}: {e}")
        
        # Create the evaluation prompt
        evaluation_prompt = f"""Here are the candidate information and design review details:

Candidate Name: {candidate.name}
Candidate Designation: {candidate.designation}

Problem Description: {design_info['problemDescription']}

Proposed Architecture: {design_info['proposedArchitecture']}

Design Tradeoffs: {design_info['designTradeoffs']}

Scalability: {design_info['scalability']}

Security Measures: {design_info['securityMeasures']}

Maintainability: {design_info['maintainability']}

Probing Questions and Answers:
{qa_text}

Please evaluate this design review comprehensively across all four dimensions."""
        
        # Gemini Setup
        client = genai.Client(api_key="AIzaSyCVSszBw1kuA1MhqxxpeSA1_11iGR2h5d8")
        
        # Create content with documents and text
        content_parts = [types.Part(text=evaluation_prompt)] + parts
        
        user_message = types.Content(
            role="user",
            parts=content_parts
        )
        
        system_instruction_text = """You are a senior software architect performing a rigorous evaluation of a candidate's architectural design and their ability to reason through system design problems under technical scrutiny. The candidate has submitted a design review document and responded to multiple technical and follow-up questions.

Your task is to:
- Critically analyze their design approach
- Evaluate the depth and practicality of their responses
- Provide clear, unbiased scores
- Offer actionable feedback to help the candidate improve

Evaluation Dimensions (with Actions and Expectations)
Evaluate the candidate across the following 4 categories. Assign scores (1–5 scale, integer) and justify each with targeted, candid observations. Then provide a comprehensive feedback summary.

1. Technical Depth (technicalDepth)
Objective: Assess the candidate's understanding of technical concepts and their ability to apply them to real-world system constraints.

Consider:
- Do they demonstrate deep knowledge of technologies, protocols, patterns (e.g., CAP theorem, caching strategies, async comms)?
- Do they appropriately handle concerns like data consistency, failure handling, service contracts?
- Are they using tools or design primitives in ways that are aligned with scale, security, or throughput goals?

Action-Oriented Scoring Guideline:
5 – Demonstrates architect-level mastery and anticipates edge cases.
3 – Solid grasp but relies on generic knowledge or lacks specificity.
1 – Uses buzzwords without practical application.

2. System Design (systemDesign)
Objective: Evaluate the structure, modularity, and scalability of the system presented.

Consider:
- How are responsibilities split between components?
- Is the architecture resilient, scalable, and change-tolerant?
- Did the candidate define clear boundaries (e.g., APIs, services, data domains)?
- Are deployment and operational considerations included (e.g., containers, CDNs, orchestration)?

Action-Oriented Scoring Guideline:
5 – Clean, extensible, and production-ready system decomposition.
3 – Good structure but missing clarity on interactions or integrations.
1 – Monolithic or naive structure with unclear component logic.

3. Tradeoff Reasoning (tradeoff)
Objective: Assess the candidate's ability to identify, evaluate, and communicate architectural trade-offs.

Consider:
- Do they present alternatives with clarity and defend their decisions?
- Are trade-offs around consistency, latency, cost, or complexity well addressed?
- Can they explain why they made each design decision?

Action-Oriented Scoring Guideline:
5 – Consistently balances multiple priorities with solid justifications.
3 – Recognizes trade-offs but decisions are shallow or one-dimensional.
1 – Makes choices without discussing any downside or mitigation.

4. Ownership & Accountability (ownership)
Objective: Gauge the candidate's ownership of their design and adaptability to feedback.

Consider:
- Did they take full accountability for choices made?
- Did they clearly articulate improvement areas or technical risks?
- Did they defend decisions without being dismissive, and revise when challenged?

Action-Oriented Scoring Guideline:
5 – Shows maturity, openness to critique, and proactive problem solving.
3 – Accepts some flaws, but lacks initiative or conviction.
1 – Defensive, vague, or unaware of system weaknesses."""

        system_instruction = types.Content(
            role="system",
            parts=[types.Part(text=system_instruction_text)]
        )
        
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EvaluationResponse,
            system_instruction=system_instruction
        )
        
        chat = client.chats.create(
            model="gemini-2.0-flash-001",
            history=[user_message],
            config=config
        )
        
        response = chat.send_message(
            "Evaluate this design review comprehensively and provide scores with detailed feedback."
        )
        
        # Parse the evaluation response
        try:
            evaluation_result = parse_evaluation(response.text)
            scores = evaluation_result.designReviewScore
            
            # Calculate overall score (average of all scores)
            overall_score = (scores.technicalDepth + scores.systemDesign + 
                           scores.tradeoff + scores.ownership) / 4.0
            
            # Update the design review with the overall score
            review.overallScore = int(overall_score * 20)  # Convert to 100 scale
            review.status = 'Reviewed'
            review.save()
            
            # Create or update DesignReviewScore record
            from .models import DesignReviewScore
            from django.utils import timezone
            
            score_record, created = DesignReviewScore.objects.get_or_create(
                designReview=review,
                defaults={
                    'overallscore': overall_score,
                    'technicalDepth': scores.technicalDepth,
                    'systemDesign': scores.systemDesign,
                    'tradeoff': scores.tradeoff,
                    'ownership': scores.ownership,
                    'feedbackSummary': scores.detailedFeedbackSummary,
                    'reviewedOn': timezone.now(),
                    'status': 'Completed'
                }
            )
            
            if not created:
                # Update existing record
                score_record.overallscore = overall_score
                score_record.technicalDepth = scores.technicalDepth
                score_record.systemDesign = scores.systemDesign
                score_record.tradeoff = scores.tradeoff
                score_record.ownership = scores.ownership
                score_record.feedbackSummary = scores.detailedFeedbackSummary
                score_record.reviewedOn = timezone.now()
                score_record.status = 'Completed'
                score_record.save()
            
            return {
                "success": True,
                "message": f"Design review {design_review_id} evaluated successfully",
                "overall_score": overall_score,
                "technical_depth": scores.technicalDepth,
                "system_design": scores.systemDesign,
                "tradeoff": scores.tradeoff,
                "ownership": scores.ownership,
                "feedback": scores.detailedFeedbackSummary
            }
            
        except Exception as parse_error:
            return f"Failed to parse evaluation response: {str(parse_error)}"
            
    except DesignReview.DoesNotExist:
        return f"Design review with ID {design_review_id} not found"
    except Exception as e:
        return f"Failed to evaluate design review {design_review_id}: {str(e)}"