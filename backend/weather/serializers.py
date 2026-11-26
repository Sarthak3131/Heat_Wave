from rest_framework import serializers

from .models import WeatherRecord


class CitySearchSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=100, trim_whitespace=True)


class CoordinateQuerySerializer(serializers.Serializer):
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-90,
        max_value=90,
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180,
    )


class ForecastQuerySerializer(CoordinateQuerySerializer):
    days = serializers.IntegerField(min_value=1, max_value=16, default=5)


class CityFilterSerializer(serializers.Serializer):
    city = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=False,
        trim_whitespace=True,
    )


class WeatherRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = (
            'id',
            'city',
            'country',
            'latitude',
            'longitude',
            'temperature_c',
            'humidity_percent',
            'apparent_temperature_c',
            'heat_index_c',
            'risk_level',
            'recorded_at',
            'created_at',
        )
        read_only_fields = fields
