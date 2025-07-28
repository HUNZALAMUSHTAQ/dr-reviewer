from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Candidate, DesignReview, DesignDocument
from .serializers import CandidateSerializer, DesignReviewSerializer
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
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
        data = request.data.copy()
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
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(design_review, context={'request': request}).data, status=status.HTTP_201_CREATED, headers=headers)
