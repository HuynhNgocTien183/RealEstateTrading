from rest_framework import serializers
from .models import Message, Favorite


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = Message
        fields = (
            'id', 'listing', 'sender', 'sender_username',
            'receiver', 'receiver_username', 'content',
            'is_read', 'created_at',
        )
        read_only_fields = ('id', 'sender', 'is_read', 'created_at')


class FavoriteSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'listing', 'listing_title', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')