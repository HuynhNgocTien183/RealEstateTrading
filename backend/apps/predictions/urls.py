from django.urls import path
from .views import PredictPriceView, PredictionHistoryView

urlpatterns = [
    path('predict/', PredictPriceView.as_view(), name='predict-price'),
    path('history/', PredictionHistoryView.as_view(), name='prediction-history'),
]