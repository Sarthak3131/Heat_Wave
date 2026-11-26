from datetime import date, timedelta
from decimal import Decimal
from unittest import TestCase
from unittest.mock import Mock

import requests

from .services.open_meteo import (
    CityNotFoundError,
    DAILY_VARIABLES,
    FORECAST_URL,
    GEOCODING_URL,
    HOURLY_VARIABLES,
    InvalidWeatherRequest,
    OpenMeteoClient,
    WeatherProviderError,
    WeatherProviderUnavailable,
)


class FakeResponse:
    def __init__(self, payload=None, status_code=200, json_error=None):
        self.payload = payload
        self.status_code = status_code
        self.json_error = json_error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f'HTTP {self.status_code}')

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.payload


class OpenMeteoClientTests(TestCase):
    def setUp(self):
        self.session = Mock()
        self.client = OpenMeteoClient(session=self.session)

    def test_search_city_strips_query_and_normalizes_locations(self):
        self.session.get.return_value = FakeResponse(
            {
                'results': [
                    {
                        'id': 123,
                        'name': 'New Delhi',
                        'latitude': 28.6139,
                        'longitude': 77.209,
                        'country': 'India',
                        'country_code': 'IN',
                        'admin1': 'Delhi',
                        'timezone': 'Asia/Kolkata',
                    }
                ]
            }
        )

        locations = self.client.search_city('  New Delhi  ')

        self.assertEqual(locations[0]['name'], 'New Delhi')
        self.assertEqual(locations[0]['latitude'], 28.6139)
        self.assertEqual(locations[0]['country'], 'India')
        self.session.get.assert_called_once_with(
            GEOCODING_URL,
            params={
                'name': 'New Delhi',
                'count': 5,
                'language': 'en',
                'format': 'json',
            },
            timeout=(3.05, 10),
        )

    def test_search_rejects_empty_or_oversized_query_before_http_call(self):
        for query in ('  ', 'x' * 101, None):
            with self.subTest(query=query):
                with self.assertRaises(InvalidWeatherRequest):
                    self.client.search_city(query)
        self.session.get.assert_not_called()

    def test_search_reports_no_matching_city(self):
        self.session.get.return_value = FakeResponse({'results': []})

        with self.assertRaises(CityNotFoundError):
            self.client.search_city('No Such City')

    def test_search_rejects_malformed_location_coordinates(self):
        self.session.get.return_value = FakeResponse(
            {'results': [{'name': 'Broken City', 'latitude': 91, 'longitude': 0}]}
        )

        with self.assertRaises(WeatherProviderError):
            self.client.search_city('Broken City')

    def test_current_weather_requests_metric_data_and_returns_timezone(self):
        self.session.get.return_value = FakeResponse(
            {
                'latitude': 28.6,
                'longitude': 77.2,
                'timezone': 'Asia/Kolkata',
                'timezone_abbreviation': 'IST',
                'utc_offset_seconds': 19800,
                'current': {
                    'time': '2026-06-01T17:30',
                    'temperature_2m': 42.5,
                    'relative_humidity_2m': 55,
                    'apparent_temperature': 45.1,
                    'wind_speed_10m': 12.3,
                    'weather_code': 2,
                    'is_day': 1,
                },
            }
        )

        result = self.client.get_current_weather(
            Decimal('28.6'),
            Decimal('77.2'),
        )

        self.assertEqual(result['timezone']['name'], 'Asia/Kolkata')
        self.assertEqual(result['timezone']['utc_offset_seconds'], 19800)
        self.assertEqual(result['current']['temperature_c'], 42.5)
        self.assertEqual(result['current']['relative_humidity_percent'], 55.0)
        self.assertTrue(result['current']['is_day'])
        self.session.get.assert_called_once()
        url = self.session.get.call_args.args[0]
        kwargs = self.session.get.call_args.kwargs
        self.assertEqual(url, FORECAST_URL)
        self.assertEqual(kwargs['params']['temperature_unit'], 'celsius')
        self.assertEqual(kwargs['params']['wind_speed_unit'], 'kmh')
        self.assertEqual(kwargs['params']['timezone'], 'auto')

    def test_current_weather_rejects_invalid_coordinates_before_http_call(self):
        for latitude, longitude in ((91, 0), (0, -181), (True, 0), (float('nan'), 0)):
            with self.subTest(latitude=latitude, longitude=longitude):
                with self.assertRaises(InvalidWeatherRequest):
                    self.client.get_current_weather(latitude, longitude)
        self.session.get.assert_not_called()

    def test_current_weather_rejects_malformed_provider_data(self):
        payload = {
            'latitude': 10,
            'longitude': 20,
            'timezone': 'Etc/UTC',
            'timezone_abbreviation': 'GMT',
            'utc_offset_seconds': 0,
            'current': {
                'time': 'not-a-time',
                'temperature_2m': 30,
                'relative_humidity_2m': 60,
                'apparent_temperature': 31,
                'wind_speed_10m': 2,
                'weather_code': 1,
                'is_day': 1,
            },
        }
        self.session.get.return_value = FakeResponse(payload)

        with self.assertRaises(WeatherProviderError):
            self.client.get_current_weather(10, 20)

    def test_forecast_returns_aligned_hourly_and_five_daily_series(self):
        start = date(2026, 6, 1)
        hourly = {
            'time': ['2026-06-01T00:00', '2026-06-01T01:00'],
            'temperature_2m': [30, 29.5],
            'relative_humidity_2m': [70, 72],
            'apparent_temperature': [34, 33],
            'wind_speed_10m': [4, 5],
            'weather_code': [2, 3],
        }
        daily = {'time': [(start + timedelta(days=index)).isoformat() for index in range(5)]}
        daily.update(
            {
                'temperature_2m_max': [40, 41, 39, 38, 37],
                'temperature_2m_min': [28, 29, 27, 26, 25],
                'sunrise': [f'{day}T05:30' for day in daily['time']],
                'sunset': [f'{day}T18:30' for day in daily['time']],
                'weather_code': [2, 3, 1, 0, 2],
            }
        )
        self.session.get.return_value = FakeResponse(
            {
                'latitude': 28.6,
                'longitude': 77.2,
                'timezone': 'Asia/Kolkata',
                'timezone_abbreviation': 'IST',
                'utc_offset_seconds': 19800,
                'hourly': hourly,
                'daily': daily,
            }
        )

        result = self.client.get_forecast(28.6, 77.2)

        self.assertEqual(result['forecast_days'], 5)
        self.assertEqual(len(result['daily']), 5)
        self.assertEqual(len(result['hourly']), 2)
        self.assertEqual(result['daily'][0]['temperature_max_c'], 40.0)
        self.assertEqual(result['hourly'][1]['relative_humidity_percent'], 72.0)
        self.assertEqual(result['timezone']['name'], 'Asia/Kolkata')
        _, kwargs = self.session.get.call_args
        self.assertEqual(kwargs['params']['forecast_days'], 5)
        self.assertEqual(kwargs['params']['hourly'], ','.join(HOURLY_VARIABLES))
        self.assertEqual(kwargs['params']['daily'], ','.join(DAILY_VARIABLES))

    def test_forecast_rejects_mismatched_hourly_arrays(self):
        payload = {
            'latitude': 10,
            'longitude': 20,
            'timezone': 'Etc/UTC',
            'timezone_abbreviation': 'GMT',
            'utc_offset_seconds': 0,
            'hourly': {
                'time': ['2026-06-01T00:00'],
                'temperature_2m': [],
                'relative_humidity_2m': [50],
                'apparent_temperature': [30],
                'wind_speed_10m': [2],
                'weather_code': [1],
            },
            'daily': {},
        }
        self.session.get.return_value = FakeResponse(payload)

        with self.assertRaises(WeatherProviderError):
            self.client.get_forecast(10, 20)

    def test_forecast_rejects_wrong_number_of_daily_periods(self):
        daily = {
            'time': ['2026-06-01'],
            'temperature_2m_max': [30],
            'temperature_2m_min': [20],
            'sunrise': ['2026-06-01T05:00'],
            'sunset': ['2026-06-01T18:00'],
            'weather_code': [1],
        }
        self.session.get.return_value = FakeResponse(
            {
                'latitude': 10,
                'longitude': 20,
                'timezone': 'Etc/UTC',
                'timezone_abbreviation': 'GMT',
                'utc_offset_seconds': 0,
                'hourly': {
                    'time': ['2026-06-01T00:00'],
                    'temperature_2m': [25],
                    'relative_humidity_2m': [50],
                    'apparent_temperature': [26],
                    'wind_speed_10m': [2],
                    'weather_code': [1],
                },
                'daily': daily,
            }
        )

        with self.assertRaises(WeatherProviderError):
            self.client.get_forecast(10, 20)

    def test_forecast_rejects_invalid_day_count(self):
        for days in (0, 17, True, 2.5):
            with self.subTest(days=days):
                with self.assertRaises(InvalidWeatherRequest):
                    self.client.get_forecast(10, 20, days=days)
        self.session.get.assert_not_called()

    def test_network_and_rate_limit_failures_are_explicit(self):
        self.session.get.side_effect = requests.Timeout('timed out')
        with self.assertRaises(WeatherProviderUnavailable):
            self.client.search_city('Delhi')

        self.session.get.side_effect = None
        self.session.get.return_value = FakeResponse(status_code=429)
        with self.assertRaises(WeatherProviderUnavailable):
            self.client.search_city('Delhi')

    def test_server_failure_is_unavailable_and_bad_request_is_provider_error(self):
        self.session.get.return_value = FakeResponse(status_code=503)
        with self.assertRaises(WeatherProviderUnavailable):
            self.client.search_city('Delhi')

        self.session.get.return_value = FakeResponse(status_code=400)
        with self.assertRaises(WeatherProviderError):
            self.client.search_city('Delhi')

    def test_invalid_json_and_provider_error_payload_are_reported(self):
        self.session.get.return_value = FakeResponse(
            json_error=ValueError('bad json'),
        )
        with self.assertRaises(WeatherProviderError):
            self.client.search_city('Delhi')

        self.session.get.return_value = FakeResponse(
            {'error': True, 'reason': 'Invalid latitude'},
        )
        with self.assertRaisesRegex(WeatherProviderError, 'Invalid latitude'):
            self.client.search_city('Delhi')
