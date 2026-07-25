from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from .models import Message, Favorite
from .serializers import MessageSerializer, FavoriteSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """
    API cho tin nhắn.
    - list: chỉ thấy tin nhắn liên quan tới mình (gửi hoặc nhận)
    - create: tự gán sender = user hiện tại
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Message.objects.filter(Q(sender=user) | Q(receiver=user))

        # Lọc theo 1 cuộc hội thoại cụ thể (theo listing + người còn lại)
        listing_id = self.request.query_params.get('listing')
        with_user = self.request.query_params.get('with_user')

        if listing_id:
            qs = qs.filter(listing_id=listing_id)
        if with_user:
            qs = qs.filter(Q(sender_id=with_user) | Q(receiver_id=with_user))

        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """
        Trả về danh sách các cuộc hội thoại (nhóm theo listing + người đối thoại),
        kèm tin nhắn mới nhất — dùng để hiển thị 'Hộp thư' như Messenger.
        """
        user = request.user
        messages = Message.objects.filter(Q(sender=user) | Q(receiver=user))

        conversations = {}
        for msg in messages:
            other_user = msg.receiver if msg.sender == user else msg.sender
            key = (msg.listing_id, other_user.id)
            if key not in conversations or msg.created_at > conversations[key].created_at:
                conversations[key] = msg

        result = MessageSerializer(list(conversations.values()), many=True).data
        return Response(result)

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Đánh dấu đã đọc toàn bộ tin nhắn trong 1 cuộc hội thoại.
        Body: { "listing": <id>, "with_user": <id> }
        """
        listing_id = request.data.get('listing')
        with_user = request.data.get('with_user')

        Message.objects.filter(
            listing_id=listing_id,
            sender_id=with_user,
            receiver=request.user,
            is_read=False,
        ).update(is_read=True)

        return Response({"detail": "Đã đánh dấu đã đọc."})


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    API cho tin yêu thích.
    - list: chỉ thấy tin yêu thích của chính mình
    - create: tự gán user = user hiện tại
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        listing_id = request.data.get('listing')
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, listing_id=listing_id
        )
        if not created:
            return Response(
                {"detail": "Tin này đã có trong danh sách yêu thích."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)