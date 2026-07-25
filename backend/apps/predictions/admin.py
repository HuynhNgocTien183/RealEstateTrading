from django.contrib import admin
from .models import PredictionLog


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'predicted_price', 'model_version', 'created_at')
    list_filter = ('model_version', 'input_property_type')
    readonly_fields = [f.name for f in PredictionLog._meta.fields]