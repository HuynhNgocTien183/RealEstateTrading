from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, FavoriteViewSet

router = DefaultRouter()
router.register('messages', MessageViewSet, basename='message')
router.register('favorites', FavoriteViewSet, basename='favorite')

urlpatterns = router.urls