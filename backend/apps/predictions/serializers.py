from rest_framework import serializers
from .models import PredictionLog


class PredictionRequestSerializer(serializers.Serializer):
    area = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
    frontage = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    access_road = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    floors = serializers.IntegerField(required=False, min_value=1, default=1)
    bedrooms = serializers.IntegerField(min_value=0, default=2)
    bathrooms = serializers.IntegerField(min_value=0, default=2)
    legal_status = serializers.CharField(required=False, allow_blank=True, default='Have certificate')
    furniture_state = serializers.CharField(required=False, allow_blank=True, default='Full')
    city = serializers.CharField(max_length=100, required=False, allow_blank=True, default='Hồ Chí Minh')
    district = serializers.CharField(max_length=100, required=False, allow_blank=True, default='Gò Vấp')
    ward = serializers.CharField(max_length=100, required=False, allow_blank=True, default='Unknown')
    listing_id = serializers.IntegerField(required=False, allow_null=True)


class PredictionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionLog
        fields = (
            'id', 'input_data', 'predicted_price', 'model_version', 'created_at',
        )
        read_only_fields = fields