import uuid
from django.conf import settings
from django.db import models


class AdvisorSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='advisor_sessions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        owner = self.user.username if self.user else 'khách'
        return f"Phiên tư vấn {self.id} ({owner})"


class AdvisorMessage(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'Người dùng'
        ASSISTANT = 'assistant', 'AI'

    session = models.ForeignKey(
        AdvisorSession,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=16, choices=Role.choices)
    content = models.TextField()
    sources = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:48]}"
