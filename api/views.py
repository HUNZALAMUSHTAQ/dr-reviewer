from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from .models import Candidate, DesignReview, DesignDocument, ProbingQuestions, DesignReviewScore
from .serializers import CandidateSerializer, DesignReviewSerializer, ProbingQuestionsSerializer, AnswerProbingQuestionsSerializer, SingleQuestionAnswerSerializer
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from .tasks import generate_probing_questions_for_review, evaluate_design_review_task
import os

# Create your views here.

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

class CandidateListView(generics.ListAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

class DesignReviewViewSet(viewsets.ModelViewSet):
    queryset = DesignReview.objects.all()
    serializer_class = DesignReviewSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        
        # Handle form data separately from files to avoid pickling issues
        data = {}
        for key, value in request.data.items():
            if key != 'files':  # Exclude files from the data dict
                data[key] = value
        
        print("HEllo")
        print(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        design_review = serializer.save()
        for f in files:
            # Save file to media folder
            media_folder = os.path.join(settings.MEDIA_ROOT, 'design_documents')
            os.makedirs(media_folder, exist_ok=True)
            file_name = f.name.replace('\\', '/').replace('\\', '/')
            file_path = f'design_documents/{file_name}'
            full_path = os.path.join(settings.MEDIA_ROOT, 'design_documents', f.name)
            with open(full_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            # Store media file URL path in db
            DesignDocument.objects.create(
                path=file_path,  # store relative media path with forward slashes
                type=os.path.splitext(f.name)[1],
                size=f.size,
                designReview=design_review,
                isProcessed='pending',
                createdOn=timezone.now(),
                updatedOn=timezone.now(),
            )
        generate_probing_questions_for_review.delay(design_review.id)
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(design_review, context={'request': request}).data, status=status.HTTP_201_CREATED, headers=headers)

@api_view(['GET'])
def get_probing_questions_by_design_review(request, design_review_id):
    """
    Get all probing questions for a specific design review ID
    """
    try:
        # Check if design review exists
        design_review = get_object_or_404(DesignReview, id=design_review_id)
        
        # Get all probing questions for this design review
        probing_questions = ProbingQuestions.objects.filter(designReview=design_review)
        
        serializer = ProbingQuestionsSerializer(probing_questions, many=True)
        
        return Response({
            'design_review_id': design_review_id,
            'questions_count': probing_questions.count(),
            'questions': serializer.data
        }, status=status.HTTP_200_OK)
        
    except DesignReview.DoesNotExist:
        return Response({
            'error': 'Design review not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def answer_probing_questions_by_design_review(request, design_review_id):
    """
    Answer all probing questions for a specific design review ID at once
    """
    try:
        # Check if design review exists
        design_review = get_object_or_404(DesignReview, id=design_review_id)
        
        # Validate request data
        serializer = AnswerProbingQuestionsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid data format',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        answers_data = serializer.validated_data.get('answers', [])
        
        if not answers_data:
            return Response({
                'error': 'No answers provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # First, validate all question IDs exist before updating any answers
        not_found_questions = []
        valid_questions = []
        
        for answer_item in answers_data:
            question_id = answer_item.get('question_id')
            answer_text = answer_item.get('answer', '')
            
            # Null checks
            if question_id is None:
                return Response({
                    'error': 'question_id is required for all answers'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Check if the specific probing question exists
                probing_question = ProbingQuestions.objects.get(
                    id=question_id, 
                    designReview=design_review
                )

                valid_questions.append({
                    'question_obj': probing_question,
                    'question_id': question_id,
                    'answer_text': answer_text
                })
                
            except ProbingQuestions.DoesNotExist:
                not_found_questions.append({
                    'question_id': question_id,
                    'status': 'not_found',
                    'error': f'Question with ID {question_id} not found for this design review'
                })
        
        # If any questions are not found, return error response
        if not_found_questions:
            return Response({
                'error': 'One or more questions not found. All answers must be for valid questions belonging to this design review.',
                'design_review_id': design_review_id,
                'total_answers_processed': len(answers_data),
                'successfully_updated': 0,
                'not_found': len(not_found_questions),
                'not_found_questions': not_found_questions
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # All questions are valid, now update all answers
        updated_questions = []
        for question_data in valid_questions:
            question_obj = question_data['question_obj']
            question_id = question_data['question_id']
            answer_text = question_data['answer_text']
            
            # Update the answer
            question_obj.answer = answer_text
            question_obj.save()
            
            updated_questions.append({
                'question_id': question_id,
                'question': question_obj.question,
                'answer': answer_text,
                'status': 'updated'
            })

        total_probing_questions = ProbingQuestions.objects.filter(designReview=design_review).count()
        total_answered_questions = ProbingQuestions.objects.filter(designReview=design_review, answer__isnull=False).count()
        if total_probing_questions <= total_answered_questions:
            # Update DesignReview status to "In Progress" 
            design_review.status = 'In Progress'
            design_review.save()
            
            # If all questions are answered, trigger evaluation task
            if total_probing_questions == total_answered_questions:
                evaluate_design_review_task.delay(design_review.id)
                print(f"All questions answered for design review {design_review.id}. Starting evaluation task.")
        
        print(total_probing_questions, total_answered_questions)
        print(f"Remaining questions: {total_probing_questions - total_answered_questions}, answered questions: {total_answered_questions}")
        response_data = {
            'design_review_id': design_review_id,
            'total_answers_processed': len(answers_data),
            'successfully_updated': len(updated_questions),
            'updated_questions': updated_questions,
            'message': 'All answers updated successfully'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except DesignReview.DoesNotExist:
        return Response({
            'error': 'Design review not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def answer_single_probing_question(request, question_id):
    """
    Answer a single probing question by question ID
    """
    try:
        # Validate request data
        serializer = SingleQuestionAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid data format',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        answer_text = serializer.validated_data.get('answer', '')
        
        # Check if the probing question exists
        try:
            probing_question = ProbingQuestions.objects.get(id=question_id)
        except ProbingQuestions.DoesNotExist:
            return Response({
                'error': 'Question not found',
                'question_id': question_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update the answer
        probing_question.answer = answer_text
        probing_question.save()
        
        # Return the updated question details
        updated_serializer = ProbingQuestionsSerializer(probing_question)

        total_probing_questions = ProbingQuestions.objects.filter(designReview=probing_question.designReview).count()
        total_answered_questions = ProbingQuestions.objects.filter(designReview=probing_question.designReview, answer__isnull=False).count()
        if total_probing_questions <= total_answered_questions:
            # Update DesignReview status to "In Progress"
            probing_question.designReview.status = 'In Progress'
            probing_question.designReview.save()
            
            # If all questions are answered, trigger evaluation task
            if total_probing_questions == total_answered_questions:
                evaluate_design_review_task.delay(probing_question.designReview.id)
                print(f"All questions answered for design review {probing_question.designReview.id}. Starting evaluation task.")
        
        print(total_probing_questions, total_answered_questions)
        print(f"Remaining questions: {total_probing_questions - total_answered_questions}, answered questions: {total_answered_questions}")
        
        return Response({
            'message': 'Answer updated successfully',
            'question': updated_serializer.data,
            'design_review_id': probing_question.designReview.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def trigger_design_review_evaluation(request, design_review_id):
    """
    Manually trigger the evaluation task for a specific design review
    """
    try:
        # Check if design review exists
        design_review = get_object_or_404(DesignReview, id=design_review_id)
        
        # Check if there are any probing questions
        total_questions = ProbingQuestions.objects.filter(designReview=design_review).count()
        if total_questions == 0:
            return Response({
                'error': 'No probing questions found for this design review'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if all questions are answered
        answered_questions = ProbingQuestions.objects.filter(
            designReview=design_review, 
            answer__isnull=False
        ).count()
        
        if answered_questions < total_questions:
            return Response({
                'error': f'Not all questions are answered. {answered_questions}/{total_questions} questions answered.',
                'total_questions': total_questions,
                'answered_questions': answered_questions,
                'remaining_questions': total_questions - answered_questions
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Trigger the evaluation task
        task_result = evaluate_design_review_task.delay(design_review_id)
        
        return Response({
            'message': 'Evaluation task triggered successfully',
            'design_review_id': design_review_id,
            'task_id': task_result.id,
            'total_questions': total_questions,
            'answered_questions': answered_questions
        }, status=status.HTTP_200_OK)
        
    except DesignReview.DoesNotExist:
        return Response({
            'error': 'Design review not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_design_review_evaluation(request, design_review_id):
    """
    Get the evaluation results for a specific design review
    """
    try:
        # Check if design review exists
        design_review = get_object_or_404(DesignReview, id=design_review_id)
        
        # Try to get the evaluation score
        try:
            score = DesignReviewScore.objects.get(designReview=design_review)
            
            return Response({
                'design_review_id': design_review_id,
                'candidate_name': design_review.candidate.name,
                'candidate_designation': design_review.candidate.designation,
                'status': design_review.status,
                'overall_score': score.overallscore,
                'scores': {
                    'technical_depth': score.technicalDepth,
                    'system_design': score.systemDesign,
                    'tradeoff': score.tradeoff,
                    'ownership': score.ownership
                },
                'feedback_summary': score.feedbackSummary,
                'reviewed_on': score.reviewedOn,
                'evaluation_status': score.status
            }, status=status.HTTP_200_OK)
            
        except DesignReviewScore.DoesNotExist:
            return Response({
                'design_review_id': design_review_id,
                'status': design_review.status,
                'message': 'Evaluation not completed yet',
                'has_evaluation': False
            }, status=status.HTTP_200_OK)
        
    except DesignReview.DoesNotExist:
        return Response({
            'error': 'Design review not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
