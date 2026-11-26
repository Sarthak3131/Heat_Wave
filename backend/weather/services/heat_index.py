import math
from decimal import Decimal
from numbers import Real

from .open_meteo import InvalidWeatherRequest
from ..models import RiskLevel


_RISK_RECOMMENDATIONS = {
    RiskLevel.LOW: (
        'Use normal precautions, stay hydrated, and take breaks as needed '
        'during prolonged outdoor activity.'
    ),
    RiskLevel.CAUTION: (
        'Limit prolonged exertion in direct sun, drink water regularly, and '
        'take breaks in a cool or shaded place.'
    ),
    RiskLevel.EXTREME_CAUTION: (
        'Reduce strenuous outdoor activity, seek shade or air conditioning, '
        'and drink water regularly. Check on people who may be more vulnerable '
        'to heat.'
    ),
    RiskLevel.DANGER: (
        'Avoid strenuous outdoor activity where possible, stay in a cool place, '
        'and drink water regularly. Check on people who may be more vulnerable '
        'to heat.'
    ),
    RiskLevel.EXTREME_DANGER: (
        'Avoid outdoor exertion where possible and remain in a cool place. '
        'Check on people who may be more vulnerable to heat and seek urgent '
        'local help if someone shows signs of a heat-related emergency.'
    ),
}


def _validated_number(value, name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
        raise InvalidWeatherRequest(f'{name} must be a finite number.')
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise InvalidWeatherRequest(f'{name} must be a finite number.') from exc
    if not math.isfinite(number):
        raise InvalidWeatherRequest(f'{name} must be a finite number.')
    if not minimum <= number <= maximum:
        raise InvalidWeatherRequest(
            f'{name} must be between {minimum} and {maximum}.'
        )
    return number


def calculate_heat_index_c(temperature_c, relative_humidity_percent):
    """Return the NOAA heat index in Celsius, or None below its applicability."""
    temperature_c = _validated_number(
        temperature_c, 'Temperature in Celsius', -100, 70
    )
    humidity = _validated_number(
        relative_humidity_percent, 'Relative humidity', 0, 100
    )

    temperature_f = temperature_c * 9 / 5 + 32
    simple_index = (
        0.5
        * (
            temperature_f
            + 61.0
            + (temperature_f - 68.0) * 1.2
            + humidity * 0.094
        )
    )
    simple_index = (simple_index + temperature_f) / 2
    if simple_index < 80:
        return None

    heat_index_f = (
        -42.379
        + 2.04901523 * temperature_f
        + 10.14333127 * humidity
        - 0.22475541 * temperature_f * humidity
        - 0.00683783 * temperature_f**2
        - 0.05481717 * humidity**2
        + 0.00122874 * temperature_f**2 * humidity
        + 0.00085282 * temperature_f * humidity**2
        - 0.00000199 * temperature_f**2 * humidity**2
    )

    if humidity < 13 and 80 <= temperature_f <= 112:
        adjustment = (
            (13 - humidity)
            / 4
            * math.sqrt((17 - abs(temperature_f - 95)) / 17)
        )
        heat_index_f -= adjustment
    elif humidity > 85 and 80 <= temperature_f <= 87:
        adjustment = ((humidity - 85) / 10) * ((87 - temperature_f) / 5)
        heat_index_f += adjustment

    return round((heat_index_f - 32) * 5 / 9, 2)


def risk_level_for_heat_index(heat_index_c):
    if heat_index_c is None:
        return None
    heat_index_c = _validated_number(heat_index_c, 'Heat Index in Celsius', -100, 100)
    if heat_index_c < 27:
        return RiskLevel.LOW
    if heat_index_c < 32:
        return RiskLevel.CAUTION
    if heat_index_c < 41:
        return RiskLevel.EXTREME_CAUTION
    if heat_index_c < 54:
        return RiskLevel.DANGER
    return RiskLevel.EXTREME_DANGER


def safety_recommendation_for_risk(risk_level):
    if risk_level is None:
        return None
    try:
        return _RISK_RECOMMENDATIONS[risk_level]
    except KeyError as exc:
        raise InvalidWeatherRequest('Unknown heat-risk category.') from exc


def assess_heat_risk(temperature_c, relative_humidity_percent):
    heat_index_c = calculate_heat_index_c(temperature_c, relative_humidity_percent)
    risk_level = risk_level_for_heat_index(heat_index_c)
    return {
        'heat_index_c': heat_index_c,
        'risk_level': risk_level,
        'recommendation': safety_recommendation_for_risk(risk_level),
    }
