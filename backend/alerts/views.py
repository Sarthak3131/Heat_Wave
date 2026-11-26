from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.pagination import StandardResultsPagination
from weather.serializers import CityFilterSerializer

from .models import HeatAlert
from .serializers import HeatAlertSerializer


class ActiveAlertListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = StandardResultsPagination

    def get(self, request):
        serializer = CityFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        alerts = HeatAlert.objects.filter(is_active=True)
        city = serializer.validated_data.get('city')
        if city:
            alerts = alerts.filter(city__icontains=city)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(alerts, request, view=self)
        data = HeatAlertSerializer(page, many=True).data
        return paginator.get_paginated_response(data)
