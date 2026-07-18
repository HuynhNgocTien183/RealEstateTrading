from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    #JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    #App routes
    path('api/users/', include('apps.users.urls')),
    path('api/listings/', include('apps.listings.urls')),
    # path('api/interactions/', include('apps.interactions.urls')),
    # path('api/predictions/', include('apps.predictions.urls')),
]