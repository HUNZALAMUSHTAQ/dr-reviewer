#!/usr/bin/env python
"""
Test script to demonstrate the new evaluation task functionality.
This script shows how to use the evaluate_design_review_task.
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dr_reviewer.settings')
django.setup()

from api.tasks import evaluate_design_review_task
from api.models import DesignReview, Candidate, DesignDocument, ProbingQuestions

def test_evaluation_task():
    """
    Test the evaluation task with a sample design review.
    """
    print("Testing Design Review Evaluation Task...")
    
    # Get an existing design review or create a test one
    try:
        # Try to get an existing design review with questions and answers
        review = DesignReview.objects.filter(
            status='Questions Generated',
            probing_questions__isnull=False
        ).first()
        
        if not review:
            print("No suitable design review found with generated questions.")
            print("Please run the question generation task first or create a design review with questions and answers.")
            return
        
        print(f"Found Design Review ID: {review.id}")
        print(f"Candidate: {review.candidate.name}")
        print(f"Status: {review.status}")
        
        # Check if there are probing questions with answers
        questions_with_answers = review.probing_questions.filter(answer__isnull=False).count()
        total_questions = review.probing_questions.count()
        
        print(f"Questions with answers: {questions_with_answers}/{total_questions}")
        
        if questions_with_answers == 0:
            print("No answered questions found. Please add answers to probing questions first.")
            return
        
        # Run the evaluation task
        print("\nRunning evaluation task...")
        result = evaluate_design_review_task(review.id)
        
        print("\nEvaluation Result:")
        print("=" * 50)
        if isinstance(result, dict) and result.get('success'):
            print(f"Overall Score: {result['overall_score']:.2f}/5.0")
            print(f"Technical Depth: {result['technical_depth']}/5")
            print(f"System Design: {result['system_design']}/5") 
            print(f"Tradeoff Reasoning: {result['tradeoff']}/5")
            print(f"Ownership: {result['ownership']}/5")
            print(f"\nDetailed Feedback:")
            print(result['feedback'])
        else:
            print(f"Error: {result}")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")

def create_sample_data():
    """
    Create sample data for testing (optional).
    """
    print("Creating sample test data...")
    
    # Create a sample candidate
    candidate, created = Candidate.objects.get_or_create(
        name="Test Candidate",
        defaults={'designation': 'Senior Software Engineer'}
    )
    
    # Create a sample design review
    review, created = DesignReview.objects.get_or_create(
        candidate=candidate,
        problemDescription="Design a scalable microservices architecture for an e-commerce platform",
        defaults={
            'proposedArchitecture': 'A microservices-based architecture with API Gateway, service mesh, and event-driven communication',
            'designTradeoffs': 'Trade-off between complexity and scalability, eventual consistency vs strong consistency',
            'scalibilty': 'Horizontal scaling with load balancers and auto-scaling groups',
            'securityMeasures': 'OAuth2, JWT tokens, API rate limiting, and encrypted communication',
            'maintainability': 'Clean code principles, comprehensive testing, and documentation',
            'status': 'Questions Generated'
        }
    )
    
    if created:
        # Add some sample probing questions with answers
        sample_questions = [
            {
                'question': 'How would you handle distributed transactions across multiple microservices?',
                'answer': 'I would implement the Saga pattern with compensating transactions to maintain data consistency across services while avoiding distributed locks.',
                'difficulty': 7
            },
            {
                'question': 'What caching strategy would you implement for this e-commerce platform?',
                'answer': 'I would use Redis for session caching, CDN for static content, and application-level caching for frequently accessed product data.',
                'difficulty': 5
            },
            {
                'question': 'How would you ensure data consistency between the order service and inventory service?',
                'answer': 'I would use event-driven architecture with eventual consistency, implementing reservation patterns for inventory management.',
                'difficulty': 6
            }
        ]
        
        for q_data in sample_questions:
            ProbingQuestions.objects.create(
                designReview=review,
                question=q_data['question'],
                answer=q_data['answer'],
                difficulty=q_data['difficulty']
            )
        
        print(f"Created sample design review with ID: {review.id}")
    else:
        print(f"Using existing design review with ID: {review.id}")
    
    return review.id

if __name__ == "__main__":
    print("Design Review Evaluation Task Test")
    print("=" * 40)
    
    # Uncomment the line below to create sample data first
    # create_sample_data()
    
    test_evaluation_task()
