from rest_framework import serializers

from .models import HeatAlert


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
