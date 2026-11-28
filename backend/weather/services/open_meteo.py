from asyncio.log import logger
from datetime import date, datetime
from decimal import Decimal
import math
from numbers import Real
import logging
import requests
logger = logging.getLogger(__name__)

GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'
FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'
DEFAULT_TIMEOUT = (3.05, 10)
HOURLY_VARIABLES = (
    'temperature_2m',
    'relative_humidity_2m',
    'apparent_temperature',
    'wind_speed_10m',
    'weather_code',
)
DAILY_VARIABLES = (
    'temperature_2m_max',
    'temperature_2m_min',
    'sunrise',
    'sunset',
    'weather_code',
)
CURRENT_VARIABLES = (
    'temperature_2m',
    'relative_humidity_2m',
    'apparent_temperature',
    'wind_speed_10m',
    'weather_code',
    'is_day',
)


class WeatherServiceError(Exception):
    """Base exception for weather lookup failures."""


class InvalidWeatherRequest(WeatherServiceError):
    """Raised when a caller provides invalid city or coordinate input."""


class CityNotFoundError(WeatherServiceError):
    """Raised when geocoding returns no matching location."""


class WeatherProviderUnavailable(WeatherServiceError):
    """Raised when Open-Meteo cannot be reached or is rate-limiting requests."""


class WeatherProviderError(WeatherServiceError):
    """Raised when Open-Meteo returns an unsuccessful or invalid response."""


def _number(value, field, *, minimum=None, maximum=None, allow_none=False):
    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
        raise WeatherProviderError(f'Open-Meteo returned invalid {field}.')

    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise WeatherProviderError(
            f'Open-Meteo returned invalid {field}.'
        ) from exc
    if not math.isfinite(number):
        raise WeatherProviderError(f'Open-Meteo returned invalid {field}.')
    if minimum is not None and number < minimum:
        raise WeatherProviderError(f'Open-Meteo returned out-of-range {field}.')
    if maximum is not None and number > maximum:
        raise WeatherProviderError(f'Open-Meteo returned out-of-range {field}.')
    return number


def _validate_time(value, field, *, date_only=False):
    if not isinstance(value, str):
        raise WeatherProviderError(f'Open-Meteo returned invalid {field}.')
    try:
        if date_only:
            date.fromisoformat(value)
        else:
            datetime.fromisoformat(value)
    except ValueError as exc:
        raise WeatherProviderError(
            f'Open-Meteo returned invalid {field}.'
        ) from exc
    return value


def _required_mapping(value, field):
    if not isinstance(value, dict):
        raise WeatherProviderError(f'Open-Meteo response is missing {field}.')
    return value


def _weather_code(value, field):
    code = _number(value, field, minimum=0, maximum=99)
    if not code.is_integer():
        raise WeatherProviderError(f'Open-Meteo returned invalid {field}.')
    return int(code)


class OpenMeteoClient:
    """Validated client for Open-Meteo geocoding and forecast APIs."""

    def __init__(self, session=None, timeout=DEFAULT_TIMEOUT):
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get_json(self, url, params):
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise WeatherProviderUnavailable(
                'The weather provider could not be reached. Please try again.'
            ) from exc

        if response.status_code == 429 or response.status_code >= 500:
            logger.warning(
                "Open-Meteo returned HTTP %s for %s",
                response.status_code,
                url,
            )
            raise WeatherProviderUnavailable(
                'The weather provider is temporarily unavailable. Please try again.'
            )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise WeatherProviderError(
                'The weather provider rejected the request.'
            ) from exc

        try:
            payload = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError) as exc:
            raise WeatherProviderError(
                'The weather provider returned invalid JSON.'
            ) from exc

        if not isinstance(payload, dict):
            raise WeatherProviderError(
                'The weather provider returned an invalid response.'
            )
        if payload.get('error'):
            reason = payload.get('reason')
            message = (
                reason.strip()
                if isinstance(reason, str) and reason.strip()
                else 'The weather provider could not process the request.'
            )
            raise WeatherProviderError(message)
        return payload

    @staticmethod
    def _coordinates(latitude, longitude):
        if (
            isinstance(latitude, bool)
            or not isinstance(latitude, (Real, Decimal))
            or not math.isfinite(float(latitude))
            or not -90 <= float(latitude) <= 90
        ):
            raise InvalidWeatherRequest('Latitude must be between -90 and 90.')
        if (
            isinstance(longitude, bool)
            or not isinstance(longitude, (Real, Decimal))
            or not math.isfinite(float(longitude))
            or not -180 <= float(longitude) <= 180
        ):
            raise InvalidWeatherRequest(
                'Longitude must be between -180 and 180.'
            )
        return float(latitude), float(longitude)

    def search_city(self, query):
        if not isinstance(query, str) or not query.strip():
            raise InvalidWeatherRequest('Enter a city name to search.')
        query = query.strip()
        if len(query) > 100:
            raise InvalidWeatherRequest('City search must be 100 characters or fewer.')

        payload = self._get_json(
            GEOCODING_URL,
            {
                'name': query,
                'count': 5,
                'language': 'en',
                'format': 'json',
            },
        )
        results = payload.get('results', [])
        if results is None or results == []:
            raise CityNotFoundError(f'No locations found for "{query}".')
        if not isinstance(results, list):
            raise WeatherProviderError(
                'The weather provider returned invalid geocoding results.'
            )

        locations = []
        for result in results:
            result = _required_mapping(result, 'location data')
            name = result.get('name')
            if not isinstance(name, str) or not name.strip():
                raise WeatherProviderError(
                    'The weather provider returned a location without a name.'
                )
            try:
                latitude, longitude = self._coordinates(
                    result.get('latitude'),
                    result.get('longitude'),
                )
            except InvalidWeatherRequest as exc:
                raise WeatherProviderError(
                    'The weather provider returned invalid coordinates.'
                ) from exc
            location = {
                'id': result.get('id'),
                'name': name.strip(),
                'latitude': latitude,
                'longitude': longitude,
            }
            for key in ('country', 'country_code', 'admin1', 'timezone'):
                value = result.get(key)
                if value is not None:
                    if not isinstance(value, str):
                        raise WeatherProviderError(
                            f'Open-Meteo returned invalid location {key}.'
                        )
                    location[key] = value
            locations.append(location)
        return locations

    def get_current_weather(self, latitude, longitude):
        latitude, longitude = self._coordinates(latitude, longitude)
        payload = self._get_json(
            FORECAST_URL,
            {
                'latitude': latitude,
                'longitude': longitude,
                'current': ','.join(CURRENT_VARIABLES),
                'timezone': 'auto',
                'temperature_unit': 'celsius',
                'wind_speed_unit': 'kmh',
            },
        )
        current = _required_mapping(payload.get('current'), 'current conditions')
        timezone_data = self._timezone(payload)
        current_data = {
            'time': _validate_time(current.get('time'), 'current timestamp'),
            'temperature_c': _number(
                current.get('temperature_2m'),
                'current temperature',
                minimum=-100,
                maximum=70,
            ),
            'relative_humidity_percent': _number(
                current.get('relative_humidity_2m'),
                'current relative humidity',
                minimum=0,
                maximum=100,
            ),
            'apparent_temperature_c': _number(
                current.get('apparent_temperature'),
                'current apparent temperature',
                minimum=-100,
                maximum=70,
            ),
            'wind_speed_kmh': _number(
                current.get('wind_speed_10m'),
                'current wind speed',
                minimum=0,
                maximum=500,
            ),
            'weather_code': _weather_code(
                current.get('weather_code'),
                'current weather code',
            ),
            'is_day': self._is_day(current.get('is_day')),
        }
        return {
            'latitude': self._number_in_payload(payload, 'latitude', -90, 90),
            'longitude': self._number_in_payload(payload, 'longitude', -180, 180),
            'timezone': timezone_data,
            'current': current_data,
        }

    def get_forecast(self, latitude, longitude, *, days=5):
        latitude, longitude = self._coordinates(latitude, longitude)
        if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 16:
            raise InvalidWeatherRequest('Forecast days must be between 1 and 16.')

        payload = self._get_json(
            FORECAST_URL,
            {
                'latitude': latitude,
                'longitude': longitude,
                'hourly': ','.join(HOURLY_VARIABLES),
                'daily': ','.join(DAILY_VARIABLES),
                'forecast_days': days,
                'timezone': 'auto',
                'temperature_unit': 'celsius',
                'wind_speed_unit': 'kmh',
            },
        )
        timezone_data = self._timezone(payload)
        hourly = self._hourly_forecast(payload, days)
        daily = self._daily_forecast(payload, days)
        return {
            'latitude': self._number_in_payload(payload, 'latitude', -90, 90),
            'longitude': self._number_in_payload(payload, 'longitude', -180, 180),
            'timezone': timezone_data,
            'forecast_days': days,
            'hourly': hourly,
            'daily': daily,
        }

    @staticmethod
    def _is_day(value):
        if value not in (0, 1) or isinstance(value, bool):
            raise WeatherProviderError('Open-Meteo returned invalid day/night data.')
        return value == 1

    @staticmethod
    def _timezone(payload):
        timezone_name = payload.get('timezone')
        timezone_abbreviation = payload.get('timezone_abbreviation')
        offset = payload.get('utc_offset_seconds')
        if not isinstance(timezone_name, str) or not timezone_name.strip():
            raise WeatherProviderError('Open-Meteo returned invalid timezone data.')
        if (
            not isinstance(timezone_abbreviation, str)
            or not timezone_abbreviation.strip()
        ):
            raise WeatherProviderError('Open-Meteo returned invalid timezone data.')
        if isinstance(offset, bool) or not isinstance(offset, int):
            raise WeatherProviderError('Open-Meteo returned invalid timezone offset.')
        return {
            'name': timezone_name,
            'abbreviation': timezone_abbreviation,
            'utc_offset_seconds': offset,
        }

    @staticmethod
    def _number_in_payload(payload, key, minimum, maximum):
        return _number(
            payload.get(key),
            f'response {key}',
            minimum=minimum,
            maximum=maximum,
        )

    @staticmethod
    def _hourly_forecast(payload, days):
        hourly = _required_mapping(payload.get('hourly'), 'hourly forecast')
        times = hourly.get('time')
        if not isinstance(times, list) or not times:
            raise WeatherProviderError('Open-Meteo returned invalid hourly timestamps.')
        for timestamp in times:
            _validate_time(timestamp, 'hourly timestamp')

        values = {}
        for provider_key in HOURLY_VARIABLES:
            series = hourly.get(provider_key)
            if not isinstance(series, list) or len(series) != len(times):
                raise WeatherProviderError(
                    f'Open-Meteo returned mismatched hourly {provider_key} data.'
                )
            values[provider_key] = series

        hourly_rows = []
        for index, timestamp in enumerate(times):
            hourly_rows.append(
                {
                    'time': timestamp,
                    'temperature_c': _number(
                        values['temperature_2m'][index],
                        'hourly temperature',
                        minimum=-100,
                        maximum=70,
                        allow_none=True,
                    ),
                    'relative_humidity_percent': _number(
                        values['relative_humidity_2m'][index],
                        'hourly relative humidity',
                        minimum=0,
                        maximum=100,
                        allow_none=True,
                    ),
                    'apparent_temperature_c': _number(
                        values['apparent_temperature'][index],
                        'hourly apparent temperature',
                        minimum=-100,
                        maximum=70,
                        allow_none=True,
                    ),
                    'wind_speed_kmh': _number(
                        values['wind_speed_10m'][index],
                        'hourly wind speed',
                        minimum=0,
                        maximum=500,
                        allow_none=True,
                    ),
                    'weather_code': (
                        None
                        if values['weather_code'][index] is None
                        else _weather_code(
                            values['weather_code'][index],
                            'hourly weather code',
                        )
                    ),
                }
            )

        if len(hourly_rows) > days * 24 + 24:
            raise WeatherProviderError(
                'Open-Meteo returned more hourly forecast data than requested.'
            )
        return hourly_rows

    @staticmethod
    def _daily_forecast(payload, days):
        daily = _required_mapping(payload.get('daily'), 'daily forecast')
        dates = daily.get('time')
        if not isinstance(dates, list) or len(dates) != days:
            raise WeatherProviderError(
                'Open-Meteo returned an unexpected number of forecast days.'
            )
        for forecast_date in dates:
            _validate_time(forecast_date, 'daily forecast date', date_only=True)

        values = {}
        for provider_key in DAILY_VARIABLES:
            series = daily.get(provider_key)
            if not isinstance(series, list) or len(series) != len(dates):
                raise WeatherProviderError(
                    f'Open-Meteo returned mismatched daily {provider_key} data.'
                )
            values[provider_key] = series

        daily_rows = []
        for index, forecast_date in enumerate(dates):
            sunrise = values['sunrise'][index]
            sunset = values['sunset'][index]
            daily_rows.append(
                {
                    'date': forecast_date,
                    'temperature_max_c': _number(
                        values['temperature_2m_max'][index],
                        'daily maximum temperature',
                        minimum=-100,
                        maximum=70,
                        allow_none=True,
                    ),
                    'temperature_min_c': _number(
                        values['temperature_2m_min'][index],
                        'daily minimum temperature',
                        minimum=-100,
                        maximum=70,
                        allow_none=True,
                    ),
                    'sunrise': (
                        _validate_time(sunrise, 'sunrise timestamp')
                        if sunrise is not None
                        else None
                    ),
                    'sunset': (
                        _validate_time(sunset, 'sunset timestamp')
                        if sunset is not None
                        else None
                    ),
                    'weather_code': (
                        None
                        if values['weather_code'][index] is None
                        else _weather_code(
                            values['weather_code'][index],
                            'daily weather code',
                        )
                    ),
                }
            )
        return daily_rows
