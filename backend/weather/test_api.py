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

    def test_history_filters_by_inclusive_date_range_and_risk_level(self):
        records = (
            ('New Delhi', '2026-06-01T23:00:00+00:00', RiskLevel.CAUTION),
            ('New Delhi', '2026-06-02T12:00:00+00:00', RiskLevel.DANGER),
            ('Mumbai', '2026-06-02T18:00:00+00:00', RiskLevel.DANGER),
            ('New Delhi', '2026-06-03T01:00:00+00:00', RiskLevel.DANGER),
        )
        for city, timestamp, risk_level in records:
            WeatherRecord.objects.create(
                city=city,
                country='India',
                latitude=Decimal('28.600000'),
                longitude=Decimal('77.200000'),
                temperature_c=Decimal('35.00'),
                humidity_percent=Decimal('60.00'),
                heat_index_c=Decimal('42.00'),
                risk_level=risk_level,
                recorded_at=datetime.fromisoformat(timestamp),
            )

        response = self.client.get(
            reverse('weather:history'),
            {
                'city': 'delhi',
                'start_date': '2026-06-02',
                'end_date': '2026-06-02',
                'risk_level': RiskLevel.DANGER,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['city'], 'New Delhi')
        self.assertEqual(response.json()['results'][0]['risk_level'], RiskLevel.DANGER)

    def test_history_rejects_invalid_dates_and_risk_level(self):
        invalid_queries = (
            {'start_date': 'not-a-date'},
            {'end_date': '2026-02-30'},
            {'start_date': '2026-06-03', 'end_date': '2026-06-02'},
            {'risk_level': 'unsafe'},
        )

        for query in invalid_queries:
            with self.subTest(query=query):
                response = self.client.get(reverse('weather:history'), query)
                self.assertEqual(response.status_code, 400)

    def test_history_analytics_returns_filtered_summary_and_distribution(self):
        records = (
            ('New Delhi', '2026-06-02T12:00:00+00:00', '30.00', '50.00', '31.00', RiskLevel.CAUTION),
            ('New Delhi', '2026-06-02T14:00:00+00:00', '40.00', '70.00', '48.00', RiskLevel.DANGER),
            ('Mumbai', '2026-06-02T16:00:00+00:00', '35.00', '60.00', '42.00', RiskLevel.DANGER),
        )
        for city, timestamp, temperature, humidity, heat_index, risk_level in records:
            WeatherRecord.objects.create(
                city=city,
                country='India',
                latitude=Decimal('28.600000'),
                longitude=Decimal('77.200000'),
                temperature_c=Decimal(temperature),
                humidity_percent=Decimal(humidity),
                heat_index_c=Decimal(heat_index),
                risk_level=risk_level,
                recorded_at=datetime.fromisoformat(timestamp),
            )

        response = self.client.get(
            reverse('weather:history-analytics'),
            {'city': 'delhi', 'start_date': '2026-06-02', 'end_date': '2026-06-02'},
        )

        self.assertEqual(response.status_code, 200)
        summary = response.json()['summary']
        self.assertEqual(summary['total_observations'], 2)
        self.assertEqual(summary['average_temperature_c'], 35.0)
        self.assertEqual(summary['maximum_temperature_c'], 40.0)
        self.assertEqual(summary['minimum_temperature_c'], 30.0)
        self.assertEqual(summary['average_humidity_percent'], 60.0)
        self.assertEqual(summary['maximum_heat_index_c'], 48.0)
        self.assertEqual(summary['risk_level_distribution'][RiskLevel.CAUTION], 1)
        self.assertEqual(summary['risk_level_distribution'][RiskLevel.DANGER], 1)
        self.assertEqual(summary['risk_level_distribution'][RiskLevel.LOW], 0)

    def test_history_analytics_returns_empty_summary(self):
        response = self.client.get(reverse('weather:history-analytics'))

        self.assertEqual(response.status_code, 200)
        summary = response.json()['summary']
        self.assertEqual(summary['total_observations'], 0)
        self.assertIsNone(summary['average_temperature_c'])
        self.assertIsNone(summary['maximum_heat_index_c'])
        self.assertEqual(summary['risk_level_distribution']['not_applicable'], 0)

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
