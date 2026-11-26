from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WeatherRecord
from .pagination import StandardResultsPagination
from .serializers import (
    CityFilterSerializer,
    CitySearchSerializer,
    CoordinateQuerySerializer,
    ForecastQuerySerializer,
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
        serializer = CityFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        records = WeatherRecord.objects.all()
        city = serializer.validated_data.get('city')
        if city:
            records = records.filter(city__icontains=city)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(records, request, view=self)
        data = WeatherRecordSerializer(page, many=True).data
        return paginator.get_paginated_response(data)
