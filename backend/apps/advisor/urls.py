from django.urls import path
from .views import AdvisorChatView, AdvisorHistoryView, AdvisorReindexView

urlpatterns = [
    path('chat/', AdvisorChatView.as_view(), name='advisor-chat'),
    path('history/', AdvisorHistoryView.as_view(), name='advisor-history'),
    path('reindex/', AdvisorReindexView.as_view(), name='advisor-reindex'),
]
