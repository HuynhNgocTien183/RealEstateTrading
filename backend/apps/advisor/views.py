from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.listings.permissions import IsAdminUser
from .models import AdvisorMessage, AdvisorSession
from .rag_service import ask, rebuild_index
from .serializers import AdvisorChatRequestSerializer, AdvisorSessionSerializer


class AdvisorChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'detail': 'Thiếu session_id.'}, status=status.HTTP_400_BAD_REQUEST)
        session = AdvisorSession.objects.filter(id=session_id).first()
        if not session:
            return Response({'detail': 'Không tìm thấy phiên chat.'}, status=status.HTTP_404_NOT_FOUND)
        if session.user_id and request.user.is_authenticated and session.user_id != request.user.id and not request.user.is_staff:
            return Response({'detail': 'Không có quyền xem phiên này.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(AdvisorSessionSerializer(session).data)

    def post(self, request):
        serializer = AdvisorChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')

        session = None
        if session_id:
            session = AdvisorSession.objects.filter(id=session_id).first()
        if session is None:
            session = AdvisorSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
            )
        elif request.user.is_authenticated and session.user_id is None:
            session.user = request.user
            session.save(update_fields=['user', 'updated_at'])

        history = [
            {'role': item.role, 'content': item.content}
            for item in session.messages.order_by('created_at')
        ]

        try:
            result = ask(message, history=history, request=request)
        except RuntimeError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            return Response({'detail': f'Lỗi tư vấn AI: {exc}'}, status=status.HTTP_400_BAD_REQUEST)

        AdvisorMessage.objects.create(session=session, role=AdvisorMessage.Role.USER, content=message)
        AdvisorMessage.objects.create(
            session=session,
            role=AdvisorMessage.Role.ASSISTANT,
            content=result['answer'],
            sources=result['sources'],
        )
        session.save(update_fields=['updated_at'])

        return Response({
            'session_id': str(session.id),
            'answer': result['answer'],
            'sources': result['sources'],
            'model': result['model'],
        }, status=status.HTTP_200_OK)


class AdvisorHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        session = AdvisorSession.objects.filter(user=request.user).first()
        if not session:
            return Response({'id': None, 'messages': []})
        return Response(AdvisorSessionSerializer(session).data)


class AdvisorReindexView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            result = rebuild_index()
        except RuntimeError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            return Response({'detail': f'Lỗi lập chỉ mục: {exc}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
