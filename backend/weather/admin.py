from django.contrib import admin

from .models import WeatherRecord


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = (
        'city',
        'country',
        'temperature_c',
        'humidity_percent',
        'heat_index_c',
        'risk_level',
        'recorded_at',
    )
    list_filter = ('risk_level', 'recorded_at')
    search_fields = ('city', 'country')
    date_hierarchy = 'recorded_at'
    ordering = ('-recorded_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (
            'Location',
            {'fields': ('city', 'country', 'latitude', 'longitude')},
        ),
        (
            'Observation',
            {
                'fields': (
                    'temperature_c',
                    'humidity_percent',
                    'apparent_temperature_c',
                    'heat_index_c',
                    'risk_level',
                    'recorded_at',
                    'created_at',
                )
            },
        ),
    )
