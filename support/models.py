from django.db import models
from user.models import Users

# Create your models here.
class Support(models.Model):
    class Type(models.TextChoices):
        PROBLEM = 'PROBLEM', 'problem'
        REPORT = 'REPORT', 'report'
        FEEDBACK = 'FEEDBACK', 'feedback' 

    class Status(models.TextChoices):
        SEND = 'Send', 'send'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    support_email = models.EmailField()
    type = models.CharField(max_length=50, choices=Type.choices)
    problem = models.TextField(blank=True, null=True, default='')
    report = models.TextField(blank=True, null=True, default='')
    feedback = models.TextField(blank=True, null=True, default='')
    url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.SEND)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.user} - {self.support_email}"

class SupportProblem(Support):
    class Meta:
        proxy = True
        verbose_name = "Problem"
        verbose_name_plural = "Problems"


class SupportReport(Support):
    class Meta:
        proxy = True
        verbose_name = "Report"
        verbose_name_plural = "Reports"


class SupportFeedback(Support):
    class Meta:
        proxy = True
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"


