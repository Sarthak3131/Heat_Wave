from rest_framework import serializers

from weather.models import RiskLevel
from weather.serializers import CityFilterSerializer

from .models import HeatAlert


class AlertQuerySerializer(CityFilterSerializer):
    risk_level = serializers.ChoiceField(
        choices=RiskLevel.values,
        required=False,
    )
    status = serializers.ChoiceField(
        choices=('active', 'inactive', 'all'),
        required=False,
        default='active',
    )


class AlertStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeatAlert
        fields = ('is_active',)


class HeatAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeatAlert
        fields = (
            'id',
            'city',
            'country',
            'latitude',
            'longitude',
            'temperature_c',
            'humidity_percent',
            'heat_index_c',
            'risk_level',
            'message',
            'recommendation',
            'forecast_time',
            'created_at',
            'updated_at',
            'is_active',
        )
        read_only_fields = fields
