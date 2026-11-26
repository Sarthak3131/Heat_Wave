from datetime import datetime, timezone as datetime_timezone
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import RiskLevel, WeatherRecord
from .services.open_meteo import (
    CityNotFoundError,
    WeatherProviderError,
    WeatherProviderUnavailable,
)


class WeatherApiTests(TestCase):
    def test_city_search_returns_provider_results(self):
        results = [{'name': 'New Delhi', 'latitude': 28.6, 'longitude': 77.2}]
        with patch('weather.views.OpenMeteoClient') as client_class:
            client_class.return_value.search_city.return_value = results

            response = self.client.get(
                reverse('weather:city-search'),
                {'q': 'Delhi'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'results': results})
        client_class.return_value.search_city.assert_called_once_with('Delhi')

    def test_city_search_validates_query_and_maps_provider_errors(self):
        response = self.client.get(reverse('weather:city-search'))
        self.assertEqual(response.status_code, 400)

        with patch('weather.views.OpenMeteoClient') as client_class:
            client_class.return_value.search_city.side_effect = CityNotFoundError(
                'No locations found.'
            )
            response = self.client.get(
                reverse('weather:city-search'),
                {'q': 'Missing City'},
            )
        self.assertEqual(response.status_code, 404)

        with patch('weather.views.OpenMeteoClient') as client_class:
            client_class.return_value.search_city.side_effect = (
                WeatherProviderUnavailable('Try again later.')
            )
            response = self.client.get(
                reverse('weather:city-search'),
                {'q': 'Delhi'},
            )
        self.assertEqual(response.status_code, 503)

    def test_current_weather_includes_heat_risk(self):
        provider_result = {
            'latitude': 28.6,
            'longitude': 77.2,
            'timezone': {'name': 'Asia/Kolkata'},
            'current': {
                'time': '2026-06-01T17:30',
                'temperature_c': 32.22,
                'relative_humidity_percent': 70.0,
                'apparent_temperature_c': 35.0,
                'wind_speed_kmh': 5.0,
                'weather_code': 2,
                'is_day': True,
            },
        }
        with patch('weather.views.OpenMeteoClient') as client_class:
            client_class.return_value.get_current_weather.return_value = (
                provider_result
            )

            response = self.client.get(
                reverse('weather:current'),
                {'latitude': '28.6', 'longitude': '77.2'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['current']['heat_risk']['heat_index_c'],
            41.06,
        )
        self.assertEqual(
            response.json()['current']['heat_risk']['risk_level'],
            RiskLevel.DANGER,
        )
        client_class.return_value.get_current_weather.assert_called_once_with(
            Decimal('28.6'),
            Decimal('77.2'),
        )

    def test_current_weather_rejects_bad_coordinates_before_provider_call(self):
        with patch('weather.views.OpenMeteoClient') as client_class:
            response = self.client.get(
                reverse('weather:current'),
                {'latitude': '91', 'longitude': '0'},
            )

        self.assertEqual(response.status_code, 400)
        client_class.assert_not_called()

    def test_current_weather_maps_provider_payload_failure(self):
        with patch('weather.views.OpenMeteoClient') as client_class:
            client_class.return_value.get_current_weather.side_effect = (
                WeatherProviderError('Invalid response.')
            )
            response = self.client.get(
                reverse('weather:current'),
                {'latitude': '28.6', 'longitude': '77.2'},
            )

        self.assertEqual(response.status_code, 502)

    def test_forecast_enriches_hourly_rows_and_forwards_days(self):
        result = {
            'latitude': 28.6,
            'longitude': 77.2,
            'timezone': {'name': 'Asia/Kolkata'},
            'forecast_days': 2,
            'hourly': [
                {
                    'time': '2026-06-01T12:00',
                    'temperature_c': 32.22,
                    'relative_humidity_percent': 70.0,
                }
            ],
            'daily': [],
        }
        with patch('weather.views.OpenMeteoClient') as client_class:
            client_class.return_value.get_forecast.return_value = result

            response = self.client.get(
                reverse('weather:forecast'),
                {
                    'latitude': '28.6',
                    'longitude': '77.2',
                    'days': '2',
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['hourly'][0]['heat_risk']['risk_level'],
            RiskLevel.DANGER,
        )
        client_class.return_value.get_forecast.assert_called_once_with(
            Decimal('28.6'),
            Decimal('77.2'),
            days=2,
        )

    def test_forecast_rejects_invalid_day_count(self):
        with patch('weather.views.OpenMeteoClient') as client_class:
            response = self.client.get(
                reverse('weather:forecast'),
                {
                    'latitude': '28.6',
                    'longitude': '77.2',
                    'days': '17',
                },
            )

        self.assertEqual(response.status_code, 400)
        client_class.assert_not_called()

    def test_history_is_paginated_and_filterable_by_city(self):
        for index in range(23):
            WeatherRecord.objects.create(
                city='New Delhi' if index < 3 else 'Mumbai',
                country='India',
                latitude=Decimal('28.600000'),
                longitude=Decimal('77.200000'),
                temperature_c=Decimal('35.00'),
                humidity_percent=Decimal('60.00'),
                recorded_at=datetime(
                    2026,
                    6,
                    1,
                    index,
                    tzinfo=datetime_timezone.utc,
                ),
            )

        response = self.client.get(
            reverse('weather:history'),
            {'city': 'delhi', 'page_size': '2'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        self.assertEqual(len(response.json()['results']), 2)
        self.assertEqual(response.json()['results'][0]['city'], 'New Delhi')

    def test_history_rejects_blank_city_filter(self):
        response = self.client.get(
            reverse('weather:history'),
            {'city': '   '},
        )

        self.assertEqual(response.status_code, 400)

    def test_history_rejects_invalid_page_size(self):
        for page_size in ('0', '101', 'invalid'):
            with self.subTest(page_size=page_size):
                response = self.client.get(
                    reverse('weather:history'),
                    {'page_size': page_size},
                )
                self.assertEqual(response.status_code, 400)

    def test_history_rejects_invalid_page_number(self):
        for page in ('0', 'invalid'):
            with self.subTest(page=page):
                response = self.client.get(
                    reverse('weather:history'),
                    {'page': page},
                )
                self.assertEqual(response.status_code, 400)

    def test_weather_routes_are_read_only(self):
        response = self.client.post(
            reverse('weather:history'),
            {'city': 'Delhi'},
        )

        self.assertEqual(response.status_code, 405)
