from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CandidateViewSet, 
    CandidateListView, 
    DesignReviewViewSet,
    get_probing_questions_by_design_review,
    answer_probing_questions_by_design_review,
    answer_single_probing_question,
    trigger_design_review_evaluation,
    get_design_review_evaluation
)

router = DefaultRouter()
router.register(r'candidate', CandidateViewSet, basename='candidate')
router.register(r'design-review', DesignReviewViewSet, basename='design-review')

urlpatterns = [
    path('', include(router.urls)),
    path('candidates/', CandidateListView.as_view(), name='candidate-list'),
    path('design-review/<int:design_review_id>/questions/', get_probing_questions_by_design_review, name='get-probing-questions'),
    path('design-review/<int:design_review_id>/questions/answer/', answer_probing_questions_by_design_review, name='answer-probing-questions'),
    path('question/<int:question_id>/answer/', answer_single_probing_question, name='answer-single-question'),
    path('design-review/<int:design_review_id>/evaluate/', trigger_design_review_evaluation, name='trigger-evaluation'),
    path('design-review/<int:design_review_id>/evaluation/', get_design_review_evaluation, name='get-evaluation'),
] 