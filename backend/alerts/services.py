from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.db import transaction

from weather.models import RiskLevel
from weather.services.heat_index import (
    assess_heat_risk,
    safety_recommendation_for_risk,
)
from weather.services.open_meteo import InvalidWeatherRequest

from .models import HeatAlert


ALERT_RISK_LEVELS = {
    RiskLevel.DANGER,
    RiskLevel.EXTREME_DANGER,
}


def _forecast_datetime(value, timezone_name):
    if not isinstance(value, str):
        raise InvalidWeatherRequest('Forecast timestamps must be ISO 8601 text.')
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise InvalidWeatherRequest(
            'Forecast timestamps must be valid ISO 8601 values.'
        ) from exc
    if parsed.utcoffset() is not None:
        return parsed
    try:
        return parsed.replace(tzinfo=ZoneInfo(timezone_name))
    except (TypeError, ZoneInfoNotFoundError) as exc:
        raise InvalidWeatherRequest('Forecast timezone must be a valid IANA zone.') from exc


def _decimal(value, name):
    if value is None or isinstance(value, bool):
        raise InvalidWeatherRequest(f'{name} must be a finite number.')
    try:
        result = Decimal(str(value))
    except (ValueError, ArithmeticError) as exc:
        raise InvalidWeatherRequest(f'{name} must be a finite number.') from exc
    if not result.is_finite():
        raise InvalidWeatherRequest(f'{name} must be a finite number.')
    return result


def generate_forecast_alerts(
    *,
    city,
    country,
    latitude,
    longitude,
    forecast,
):
    """Create/update severe forecast alerts and deactivate resolved periods."""
    if not isinstance(city, str) or not city.strip():
        raise InvalidWeatherRequest('City must not be blank.')
    if len(city.strip()) > 120:
        raise InvalidWeatherRequest('City must be 120 characters or fewer.')
    if not isinstance(country, str):
        raise InvalidWeatherRequest('Country must be text.')
    if len(country.strip()) > 120:
        raise InvalidWeatherRequest('Country must be 120 characters or fewer.')
    if not isinstance(forecast, dict):
        raise InvalidWeatherRequest('Forecast must be a provider response object.')

    city = city.strip()
    country = country.strip()
    location_name = f'{city}, {country}' if country else city
    latitude = _decimal(latitude, 'Latitude')
    longitude = _decimal(longitude, 'Longitude')
    if not Decimal('-90') <= latitude <= Decimal('90'):
        raise InvalidWeatherRequest('Latitude must be between -90 and 90.')
    if not Decimal('-180') <= longitude <= Decimal('180'):
        raise InvalidWeatherRequest('Longitude must be between -180 and 180.')
    timezone_data = forecast.get('timezone')
    if not isinstance(timezone_data, dict):
        raise InvalidWeatherRequest('Forecast timezone data is required.')
    timezone_name = timezone_data.get('name')
    if not isinstance(timezone_name, str) or not timezone_name.strip():
        raise InvalidWeatherRequest('Forecast timezone must be provided.')
    try:
        ZoneInfo(timezone_name)
    except (TypeError, ZoneInfoNotFoundError) as exc:
        raise InvalidWeatherRequest('Forecast timezone must be a valid IANA zone.') from exc

    hourly = forecast.get('hourly')
    if not isinstance(hourly, list):
        raise InvalidWeatherRequest('Forecast hourly data must be a list.')

    periods = {}
    evaluated_times = set()
    eligible = {}
    for item in hourly:
        if not isinstance(item, dict):
            raise InvalidWeatherRequest('Forecast hourly rows must be objects.')
        forecast_time = _forecast_datetime(item.get('time'), timezone_name)
        periods[forecast_time] = item
        temperature = item.get('temperature_c')
        humidity = item.get('relative_humidity_percent')
        if temperature is None or humidity is None:
            continue
        evaluated_times.add(forecast_time)
        assessment = assess_heat_risk(temperature, humidity)
        risk_level = assessment['risk_level']
        if risk_level not in ALERT_RISK_LEVELS:
            continue
        eligible[forecast_time] = {
            'temperature_c': _decimal(temperature, 'Temperature'),
            'humidity_percent': _decimal(humidity, 'Relative humidity'),
            'heat_index_c': _decimal(
                assessment['heat_index_c'],
                'Heat Index',
            ),
            'risk_level': risk_level,
            'message': (
                f'{risk_level.label} heat risk is forecast for '
                f'{location_name} at {forecast_time.isoformat()}.'
            )[:500],
            'recommendation': safety_recommendation_for_risk(risk_level),
        }

    if not periods:
        return {'created': 0, 'updated': 0, 'deactivated': 0}

    with transaction.atomic():
        existing = list(
            HeatAlert.objects.select_for_update().filter(
                city=city,
                country=country,
                forecast_time__in=periods,
                is_active=True,
            )
        )
        existing_by_time = {alert.forecast_time: alert for alert in existing}
        created = 0
        updated = 0
        deactivated = 0

        for forecast_time, values in eligible.items():
            alert = existing_by_time.get(forecast_time)
            if alert is not None:
                for field, value in values.items():
                    setattr(alert, field, value)
                alert.latitude = latitude
                alert.longitude = longitude
                alert.save(
                    update_fields=[
                        'temperature_c',
                        'humidity_percent',
                        'heat_index_c',
                        'risk_level',
                        'message',
                        'recommendation',
                        'latitude',
                        'longitude',
                        'updated_at',
                    ]
                )
                updated += 1
                continue

            _, was_created = HeatAlert.objects.get_or_create(
                city=city,
                country=country,
                forecast_time=forecast_time,
                is_active=True,
                defaults={
                    **values,
                    'latitude': latitude,
                    'longitude': longitude,
                },
            )
            created += int(was_created)
            updated += int(not was_created)

        resolved_times = evaluated_times - set(eligible)
        if resolved_times:
            deactivated = HeatAlert.objects.filter(
                city=city,
                country=country,
                forecast_time__in=resolved_times,
                is_active=True,
            ).update(is_active=False)

    return {
        'created': created,
        'updated': updated,
        'deactivated': deactivated,
    }
