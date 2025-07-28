from django.db import models

# Create your models here.

class Candidate(models.Model):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    createdOn = models.DateTimeField(auto_now_add=True)
    updatedOn = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class DesignReview(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Incomplete', 'Incomplete'),
        ('Completed', 'Completed'),
    ]
    problemDescription = models.TextField()
    proposedArchitecture = models.TextField()
    designTradeoffs = models.TextField()
    scalibilty = models.TextField()
    securityMeasures = models.TextField()
    maintainability = models.TextField()
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='design_reviews')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    submissionDate = models.DateTimeField(auto_now_add=True)
    overallScore = models.IntegerField(null=True, blank=True)
    createdOn = models.DateTimeField(auto_now_add=True)
    updatedOn = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"DesignReview {self.id} for {self.candidate.name}"

class DesignDocument(models.Model):
    PROCESS_STATUS_CHOICES = [
        ('error', 'Error'),
        ('pending', 'Pending'),
        ('done', 'Done'),
    ]
    isProcessed = models.CharField(max_length=10, choices=PROCESS_STATUS_CHOICES, default='pending')
    path = models.CharField(max_length=255)  # store static file path as string
    type = models.CharField(max_length=10)
    size = models.PositiveIntegerField()
    designReview = models.ForeignKey(DesignReview, on_delete=models.CASCADE, related_name='documents')
    createdOn = models.DateTimeField(auto_now_add=True)
    updatedOn = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.path

class ProbingQuestions(models.Model):
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    difficulty = models.IntegerField()
    designReview = models.ForeignKey(DesignReview, on_delete=models.CASCADE, related_name='probing_questions')
    createdOn = models.DateTimeField(auto_now_add=True)
    updatedOn = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

class DesignReviewScore(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Incomplete', 'Incomplete'),
        ('Completed', 'Completed'),
    ]
    overallscore = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reviewedOn = models.DateTimeField()
    technicalDepth = models.IntegerField()
    systemDesign = models.IntegerField()
    tradeoff = models.IntegerField()
    ownership = models.IntegerField()
    feedbackSummary = models.TextField()
    designReview = models.ForeignKey(DesignReview, on_delete=models.CASCADE, related_name='scores')
    createdOn = models.DateTimeField(auto_now_add=True)
    updatedOn = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Score for Review {self.designReview.id}"
