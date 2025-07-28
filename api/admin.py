from django.contrib import admin
from .models import Candidate, DesignReview, DesignDocument, ProbingQuestions, DesignReviewScore

admin.site.register(Candidate)
admin.site.register(DesignReview)
admin.site.register(DesignDocument)
admin.site.register(ProbingQuestions)
admin.site.register(DesignReviewScore)
