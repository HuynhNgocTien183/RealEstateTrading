from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .serializers import PredictionRequestSerializer, PredictionLogSerializer
from .models import PredictionLog
from .ml_service import predict_price
from apps.listings.models import Listing


class PredictPriceView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PredictionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            predicted_price, model_version = predict_price(
                area=data['area'],
                frontage=data.get('frontage'),
                access_road=data.get('access_road'),
                floors=data.get('floors'),
                bedrooms=data['bedrooms'],
                bathrooms=data['bathrooms'],
                legal_status=data.get('legal_status'),
                furniture_state=data.get('furniture_state'),
                city=data.get('city'),
                district=data.get('district'),
            )
        except RuntimeError as e:
            return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        listing = None
        listing_id = data.get('listing_id')
        if listing_id:
            listing = Listing.objects.filter(id=listing_id).first()
            if listing:
                listing.predicted_price = predicted_price
                listing.save(update_fields=['predicted_price'])

        log = PredictionLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            listing=listing,
            input_area=data['area'],
            input_city=data.get('city', ''),
            input_district=data.get('district', ''),
            input_bedrooms=data['bedrooms'],
            input_bathrooms=data['bathrooms'],
            input_property_type=data.get('property_type', ''),
            predicted_price=predicted_price,
            model_version=model_version,
        )

        return Response({
            "predicted_price": predicted_price,
            "model_version": model_version,
            "log_id": log.id,
        }, status=status.HTTP_200_OK)


class PredictionHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logs = PredictionLog.objects.filter(user=request.user)
        return Response(PredictionLogSerializer(logs, many=True).data)