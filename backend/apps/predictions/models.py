from django.db import models
from django.conf import settings


class PredictionLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='prediction_logs',
    )
    listing = models.ForeignKey(
        'listings.Listing', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='prediction_logs',
    )

    input_area = models.DecimalField(max_digits=10, decimal_places=2)
    input_city = models.CharField(max_length=100)
    input_district = models.CharField(max_length=100)
    input_bedrooms = models.PositiveSmallIntegerField()
    input_bathrooms = models.PositiveSmallIntegerField()
    input_property_type = models.CharField(max_length=20)

    predicted_price = models.DecimalField(max_digits=15, decimal_places=2)
    model_version = models.CharField(max_length=50, default='dummy-v0')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Dự đoán #{self.id} - {self.predicted_price:,.0f} VNĐ"