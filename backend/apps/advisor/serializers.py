from rest_framework import serializers
from .models import AdvisorMessage, AdvisorSession


class AdvisorChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000, trim_whitespace=True)
    session_id = serializers.UUIDField(required=False, allow_null=True)


class AdvisorMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvisorMessage
        fields = ('id', 'role', 'content', 'sources', 'created_at')
        read_only_fields = fields


class AdvisorSessionSerializer(serializers.ModelSerializer):
    messages = AdvisorMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AdvisorSession
        fields = ('id', 'created_at', 'updated_at', 'messages')
        read_only_fields = fields
