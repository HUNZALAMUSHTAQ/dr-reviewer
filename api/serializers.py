from rest_framework import serializers
from .models import Candidate, DesignReview, DesignDocument, ProbingQuestions, DesignReviewScore
from django.conf import settings

class DesignDocumentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = DesignDocument
        fields = ['id', 'isProcessed', 'url', 'type', 'size', 'createdOn', 'updatedOn']

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.path:
            url = settings.MEDIA_URL + obj.path if not obj.path.startswith(settings.MEDIA_URL) else obj.path
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

class ProbingQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProbingQuestions
        fields = ['id', 'question', 'answer', 'difficulty', 'createdOn', 'updatedOn']

class ProbingQuestionAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.CharField(max_length=5000, allow_blank=True, required=False)

class AnswerProbingQuestionsSerializer(serializers.Serializer):
    answers = ProbingQuestionAnswerSerializer(many=True)

class SingleQuestionAnswerSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=5000, allow_blank=True, required=False)

class DesignReviewScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignReviewScore
        fields = ['id', 'overallscore', 'status', 'reviewedOn', 'technicalDepth', 'systemDesign', 'tradeoff', 'ownership', 'feedbackSummary', 'createdOn', 'updatedOn']

class DesignReviewSerializer(serializers.ModelSerializer):
    documents = DesignDocumentSerializer(many=True, read_only=True)
    probing_questions = ProbingQuestionsSerializer(many=True, read_only=True)
    scores = DesignReviewScoreSerializer(many=True, read_only=True)

    class Meta:
        model = DesignReview
        fields = [
            'id', 'problemDescription', 'proposedArchitecture', 'designTradeoffs', 'scalibilty',
            'securityMeasures', 'maintainability', 'candidate', 'status', 'submissionDate',
            'overallScore', 'createdOn', 'updatedOn', 'documents', 'probing_questions', 'scores'
        ]

class CandidateSerializer(serializers.ModelSerializer):
    design_reviews = DesignReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'name', 'designation', 'createdOn', 'updatedOn', 'design_reviews'] 