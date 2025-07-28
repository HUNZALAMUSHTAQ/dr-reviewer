from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidateViewSet, CandidateListView, DesignReviewViewSet

router = DefaultRouter()
router.register(r'candidate', CandidateViewSet, basename='candidate')
router.register(r'design-review', DesignReviewViewSet, basename='design-review')

urlpatterns = [
    path('', include(router.urls)),
    path('candidates/', CandidateListView.as_view(), name='candidate-list'),
] 