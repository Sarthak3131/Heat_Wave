from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class RiskLevel(models.TextChoices):
    LOW = 'low', 'Low'
    CAUTION = 'caution', 'Caution'
    EXTREME_CAUTION = 'extreme_caution', 'Extreme Caution'
    DANGER = 'danger', 'Danger'
    EXTREME_DANGER = 'extreme_danger', 'Extreme Danger'


class WeatherRecord(models.Model):
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
        help_text='Ambient air temperature in degrees Celsius.',
    )
    humidity_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Relative humidity as a percentage.',
    )
    apparent_temperature_c = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(-100), MaxValueValidator(70)],
        help_text='Provider-reported apparent temperature in degrees Celsius.',
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
        blank=True,
        help_text='Indicative Heat Index category; blank when not applicable.',
    )
    recorded_at = models.DateTimeField(
        default=timezone.now,
        help_text='Timestamp of the weather observation.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(
                fields=['city', 'recorded_at'],
                name='weather_city_recorded_idx',
            ),
            models.Index(
                fields=['risk_level', 'recorded_at'],
                name='weather_risk_recorded_idx',
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(latitude__gte=-90, latitude__lte=90),
                name='weather_latitude_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(longitude__gte=-180, longitude__lte=180),
                name='weather_longitude_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(
                    temperature_c__gte=-100,
                    temperature_c__lte=70,
                ),
                name='weather_temperature_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(
                    humidity_percent__gte=0,
                    humidity_percent__lte=100,
                ),
                name='weather_humidity_valid',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(apparent_temperature_c__isnull=True)
                    | models.Q(
                        apparent_temperature_c__gte=-100,
                        apparent_temperature_c__lte=70,
                    )
                ),
                name='weather_apparent_temp_valid',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(heat_index_c__isnull=True)
                    | models.Q(heat_index_c__gte=-100, heat_index_c__lte=100)
                ),
                name='weather_heat_index_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(
                    risk_level__in=[
                        RiskLevel.LOW,
                        RiskLevel.CAUTION,
                        RiskLevel.EXTREME_CAUTION,
                        RiskLevel.DANGER,
                        RiskLevel.EXTREME_DANGER,
                        '',
                    ]
                ),
                name='weather_risk_level_valid',
            ),
        ]

    def clean(self):
        self.city = self.city.strip()
        self.country = self.country.strip()
        if not self.city:
            raise ValidationError({'city': 'City cannot be blank.'})

    def __str__(self):
        return f'{self.city}, {self.country} at {self.recorded_at:%Y-%m-%d %H:%M}'
