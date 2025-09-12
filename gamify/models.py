

# Create your models here.
from django.db import models
from django.conf import settings
from content.models import Lesson

class PointsTransaction(models.Model):
    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='transactions')
    points = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.unique_name} +{self.points} pts"

class Progress(models.Model):
    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    progress = models.FloatField(default=0.0, help_text="0.0-100.0")
    last_interaction = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('profile','lesson')

    def __str__(self):
        return f"{self.profile.unique_name}: {self.lesson.title} {self.progress}%"

class Badge(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='badges/', null=True, blank=True)
    criteria = models.JSONField(default=dict, blank=True)  # e.g., {"points":100}

    def __str__(self):
        return self.title

class UserBadge(models.Model):
    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'badge')
