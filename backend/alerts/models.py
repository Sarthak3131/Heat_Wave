from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from weather.models import RiskLevel


class HeatAlert(models.Model):
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120, blank=True, default='')
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    temperature_c = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(-100), MaxValueValidator(70)],
        help_text='Forecast ambient air temperature in degrees Celsius.',
    )
    humidity_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Forecast relative humidity as a percentage.',
    )
    heat_index_c = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text='Calculated Heat Index in degrees Celsius, when applicable.',
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
    )
    message = models.CharField(max_length=500)
    recommendation = models.TextField()
    forecast_time = models.DateTimeField(
        help_text='Timezone-aware timestamp of the forecast condition.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['forecast_time', 'city']
        indexes = [
            models.Index(
                fields=['is_active', 'forecast_time'],
                name='alert_active_forecast_idx',
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(latitude__gte=-90, latitude__lte=90),
                name='alert_latitude_valid',
            ),
            models.CheckConstraint(
                condition=Q(longitude__gte=-180, longitude__lte=180),
                name='alert_longitude_valid',
            ),
            models.CheckConstraint(
                condition=Q(
                    temperature_c__gte=-100,
                    temperature_c__lte=70,
                ),
                name='alert_temperature_valid',
            ),
            models.CheckConstraint(
                condition=Q(
                    humidity_percent__gte=0,
                    humidity_percent__lte=100,
                ),
                name='alert_humidity_valid',
            ),
            models.CheckConstraint(
                condition=(
                    Q(heat_index_c__isnull=True)
                    | Q(heat_index_c__gte=-100, heat_index_c__lte=100)
                ),
                name='alert_heat_index_valid',
            ),
            models.CheckConstraint(
                condition=Q(
                    risk_level__in=[
                        RiskLevel.LOW,
                        RiskLevel.CAUTION,
                        RiskLevel.EXTREME_CAUTION,
                        RiskLevel.DANGER,
                        RiskLevel.EXTREME_DANGER,
                    ]
                ),
                name='alert_risk_level_valid',
            ),
            models.UniqueConstraint(
                fields=['city', 'country', 'forecast_time'],
                condition=Q(is_active=True),
                name='alert_unique_active_forecast',
            ),
        ]

    def clean(self):
        self.city = self.city.strip()
        self.country = self.country.strip()
        if not self.city:
            raise ValidationError({'city': 'City cannot be blank.'})

    def __str__(self):
        return f'{self.city}, {self.country} alert at {self.forecast_time:%Y-%m-%d %H:%M}'
