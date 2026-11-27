from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.pagination import StandardResultsPagination

from .models import HeatAlert
from .serializers import AlertQuerySerializer, AlertStatusSerializer, HeatAlertSerializer


def _filtered_alerts(values, *, include_inactive=False):
    alerts = HeatAlert.objects.all() if include_inactive else HeatAlert.objects.filter(is_active=True)
    city = values.get('city')
    if city:
        alerts = alerts.filter(city__icontains=city)
    risk_level = values.get('risk_level')
    if risk_level:
        alerts = alerts.filter(risk_level=risk_level)
    if include_inactive:
        alert_status = values.get('status', 'all')
        if alert_status != 'all':
            alerts = alerts.filter(is_active=alert_status == 'active')
    return alerts


class ActiveAlertListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = StandardResultsPagination

    def get(self, request):
        serializer = AlertQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        alerts = _filtered_alerts(serializer.validated_data)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(alerts, request, view=self)
        data = HeatAlertSerializer(page, many=True).data
        return paginator.get_paginated_response(data)


class AlertManagementListView(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsPagination

    def get(self, request):
        serializer = AlertQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        alerts = _filtered_alerts(serializer.validated_data, include_inactive=True)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(alerts, request, view=self)
        return paginator.get_paginated_response(HeatAlertSerializer(page, many=True).data)


class AlertManagementDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, alert_id):
        try:
            alert = HeatAlert.objects.get(pk=alert_id)
        except HeatAlert.DoesNotExist:
            return Response({'detail': 'Alert not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AlertStatusSerializer(alert, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(HeatAlertSerializer(alert).data)
