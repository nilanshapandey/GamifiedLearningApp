

# Create your models here.
from django.db import models

class Device(models.Model):
    identifier = models.CharField(max_length=255, unique=True)  # e.g., generated uuid
    label = models.CharField(max_length=255, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.label or self.identifier

class ChangeLog(models.Model):
    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='changelogs')
    model_name = models.CharField(max_length=255)
    object_id = models.CharField(max_length=255)
    change = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_name} {self.object_id} ({'synced' if self.synced else 'pending'})"
