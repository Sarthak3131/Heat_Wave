from django.contrib import admin, messages

from .models import HeatAlert


@admin.register(HeatAlert)
class HeatAlertAdmin(admin.ModelAdmin):
    list_display = (
        'city',
        'country',
        'risk_level',
        'heat_index_c',
        'forecast_time',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'risk_level', 'forecast_time')
    search_fields = ('city', 'country', 'message')
    date_hierarchy = 'forecast_time'
    ordering = ('forecast_time', 'city')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ('deactivate_alerts',)

    fieldsets = (
        (
            'Location',
            {'fields': ('city', 'country', 'latitude', 'longitude')},
        ),
        (
            'Forecast risk',
            {
                'fields': (
                    'temperature_c',
                    'humidity_percent',
                    'heat_index_c',
                    'risk_level',
                    'forecast_time',
                    'message',
                    'recommendation',
                )
            },
        ),
        (
            'Alert status',
            {'fields': ('is_active', 'created_at', 'updated_at')},
        ),
    )

    @admin.action(
        permissions=['change'],
        description='Deactivate selected forecast alerts',
    )
    def deactivate_alerts(self, request, queryset):
        updated_count = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(
            request,
            f'{updated_count} active alert(s) deactivated.',
            messages.SUCCESS,
        )
