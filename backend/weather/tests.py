from datetime import datetime, timezone as datetime_timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import RiskLevel, WeatherRecord


class WeatherRecordModelTests(TestCase):
    def setUp(self):
        self.record_data = {
            'city': '  New Delhi  ',
            'country': ' India ',
            'latitude': Decimal('28.613900'),
            'longitude': Decimal('77.209000'),
            'temperature_c': Decimal('42.50'),
            'humidity_percent': Decimal('55.00'),
            'apparent_temperature_c': Decimal('44.00'),
            'heat_index_c': Decimal('45.25'),
            'risk_level': RiskLevel.DANGER,
            'recorded_at': datetime(2026, 6, 1, 12, tzinfo=datetime_timezone.utc),
        }

    def test_valid_record_normalizes_location_and_persists(self):
        record = WeatherRecord(**self.record_data)
        record.full_clean()
        record.save()

        stored = WeatherRecord.objects.get(pk=record.pk)
        self.assertEqual(stored.city, 'New Delhi')
        self.assertEqual(stored.country, 'India')
        self.assertEqual(stored.temperature_c, Decimal('42.50'))
        self.assertEqual(stored.risk_level, RiskLevel.DANGER)
        self.assertIsNotNone(stored.created_at)

    def test_invalid_coordinates_and_humidity_fail_validation(self):
        for field, value in (
            ('latitude', Decimal('91')),
            ('longitude', Decimal('-181')),
            ('humidity_percent', Decimal('100.01')),
        ):
            with self.subTest(field=field):
                record = WeatherRecord(**{**self.record_data, field: value})
                with self.assertRaises(ValidationError):
                    record.full_clean()

    def test_blank_city_after_trimming_fails_validation(self):
        record = WeatherRecord(**{**self.record_data, 'city': '   '})

        with self.assertRaises(ValidationError) as error:
            record.full_clean()

        self.assertIn('city', error.exception.message_dict)

    def test_database_rejects_out_of_range_humidity(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WeatherRecord.objects.create(
                    **{
                        **self.record_data,
                        'city': 'Invalid humidity',
                        'humidity_percent': Decimal('101'),
                    }
                )

    def test_indexes_cover_city_and_risk_time_queries(self):
        index_fields = {
            tuple(index.fields)
            for index in WeatherRecord._meta.indexes
        }

        self.assertIn(('city', 'recorded_at'), index_fields)
        self.assertIn(('risk_level', 'recorded_at'), index_fields)


class WeatherRecordAdminTests(TestCase):
    def test_anonymous_user_cannot_access_weather_admin(self):
        response = self.client.get(
            reverse('admin:weather_weatherrecord_changelist'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin:login'), response.url)

    def test_superuser_can_view_weather_records(self):
        user = get_user_model().objects.create_superuser(
            username='weather-admin',
            email='weather-admin@example.test',
            password='unused-test-password',
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse('admin:weather_weatherrecord_changelist'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'risk_level')
