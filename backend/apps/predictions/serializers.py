from rest_framework import serializers
from .models import PredictionLog


class PredictionRequestSerializer(serializers.Serializer):
    area = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
    frontage = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    access_road = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    floors = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    bedrooms = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    bathrooms = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    legal_status = serializers.CharField(required=False, allow_blank=True, default='Have certificate')
    furniture_state = serializers.CharField(required=False, allow_blank=True, default='Full')
    city = serializers.CharField(max_length=100, required=False, allow_blank=True, default='Hồ Chí Minh')
    district = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    ward = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    address = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    street = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    house_position = serializers.CharField(max_length=20, required=False, allow_blank=True, default='Unknown')
    property_type = serializers.CharField(max_length=20, required=False, allow_blank=True, default='house')
    listing_id = serializers.IntegerField(required=False, allow_null=True)


class PredictionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionLog
        fields = (
            'id', 'input_data', 'predicted_price', 'model_version', 'created_at',
        )
        read_only_fields = fields