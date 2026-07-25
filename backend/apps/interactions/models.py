from django.db import models
from django.conf import settings


class Message(models.Model):
    listing = models.ForeignKey(
        'listings.Listing', on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:30]}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites'
    )
    listing = models.ForeignKey(
        'listings.Listing', on_delete=models.CASCADE, related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')   # 1 user chỉ lưu yêu thích 1 tin đăng 1 lần
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} thích {self.listing}"