from django.db.models import Avg, Count, Max, Min
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RiskLevel, WeatherRecord
from .pagination import StandardResultsPagination
from .serializers import (
    CitySearchSerializer,
    CoordinateQuerySerializer,
    ForecastQuerySerializer,
    HistoricalWeatherQuerySerializer,
    WeatherRecordSerializer,
)
from .services.heat_index import assess_heat_risk
from .services.open_meteo import (
    CityNotFoundError,
    InvalidWeatherRequest,
    OpenMeteoClient,
    WeatherProviderError,
    WeatherProviderUnavailable,
)


def _service_error_response(error):
    if isinstance(error, InvalidWeatherRequest):
        response_status = status.HTTP_400_BAD_REQUEST
    elif isinstance(error, CityNotFoundError):
        response_status = status.HTTP_404_NOT_FOUND
    elif isinstance(error, WeatherProviderUnavailable):
        response_status = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        response_status = status.HTTP_502_BAD_GATEWAY
    return Response({'detail': str(error)}, status=response_status)


def _heat_risk(temperature_c, humidity_percent):
    if temperature_c is None or humidity_percent is None:
        return {
            'heat_index_c': None,
            'risk_level': None,
            'recommendation': None,
        }
    return assess_heat_risk(temperature_c, humidity_percent)


def _filtered_weather_records(values):
    records = WeatherRecord.objects.all()
    city = values.get('city')
    if city:
        records = records.filter(city__icontains=city)
    start_date = values.get('start_date')
    if start_date:
        records = records.filter(recorded_at__date__gte=start_date)
    end_date = values.get('end_date')
    if end_date:
        records = records.filter(recorded_at__date__lte=end_date)
    risk_level = values.get('risk_level')
    if risk_level:
        records = records.filter(risk_level=risk_level)
    return records


def _risk_level_distribution(records):
    distribution = {risk_level: 0 for risk_level in RiskLevel.values}
    distribution['not_applicable'] = 0
    for row in records.values('risk_level').annotate(count=Count('id')):
        key = row['risk_level'] or 'not_applicable'
        distribution[key] = row['count']
    return distribution


class CitySearchView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = CitySearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            results = OpenMeteoClient().search_city(serializer.validated_data['q'])
        except (
            InvalidWeatherRequest,
            CityNotFoundError,
            WeatherProviderUnavailable,
            WeatherProviderError,
        ) as error:
            return _service_error_response(error)
        return Response({'results': results})


class CurrentWeatherView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = CoordinateQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        try:
            weather = OpenMeteoClient().get_current_weather(
                values['latitude'],
                values['longitude'],
            )
        except (
            InvalidWeatherRequest,
            CityNotFoundError,
            WeatherProviderUnavailable,
            WeatherProviderError,
        ) as error:
            return _service_error_response(error)
        current = weather['current']
        current['heat_risk'] = _heat_risk(
            current['temperature_c'],
            current['relative_humidity_percent'],
        )
        return Response(weather)


class ForecastView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = ForecastQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        try:
            forecast = OpenMeteoClient().get_forecast(
                values['latitude'],
                values['longitude'],
                days=values['days'],
            )
        except (
            InvalidWeatherRequest,
            CityNotFoundError,
            WeatherProviderUnavailable,
            WeatherProviderError,
        ) as error:
            return _service_error_response(error)
        for hour in forecast['hourly']:
            hour['heat_risk'] = _heat_risk(
                hour['temperature_c'],
                hour['relative_humidity_percent'],
            )
        return Response(forecast)


class WeatherHistoryView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = StandardResultsPagination

    def get(self, request):
        serializer = HistoricalWeatherQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        records = _filtered_weather_records(values)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(records, request, view=self)
        data = WeatherRecordSerializer(page, many=True).data
        return paginator.get_paginated_response(data)


class WeatherHistoryAnalyticsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = HistoricalWeatherQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        records = _filtered_weather_records(serializer.validated_data)
        summary = records.aggregate(
            average_temperature_c=Avg('temperature_c'),
            maximum_temperature_c=Max('temperature_c'),
            minimum_temperature_c=Min('temperature_c'),
            average_humidity_percent=Avg('humidity_percent'),
            maximum_heat_index_c=Max('heat_index_c'),
            total_observations=Count('id'),
        )
        summary['risk_level_distribution'] = _risk_level_distribution(records)
        return Response({'summary': summary})
