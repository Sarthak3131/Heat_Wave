from datetime import datetime, timedelta, timezone as datetime_timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from weather.models import RiskLevel

from .models import HeatAlert


class HeatAlertModelTests(TestCase):
    def setUp(self):
        self.forecast_time = datetime(
            2026,
            6,
            1,
            12,
            tzinfo=datetime_timezone.utc,
        )
        self.alert_data = {
            'city': '  New Delhi  ',
            'country': ' India ',
            'latitude': Decimal('28.613900'),
            'longitude': Decimal('77.209000'),
            'temperature_c': Decimal('42.50'),
            'humidity_percent': Decimal('55.00'),
            'heat_index_c': Decimal('45.25'),
            'risk_level': RiskLevel.DANGER,
            'message': 'Dangerous forecast heat stress expected.',
            'recommendation': 'Limit outdoor activity and drink water.',
            'forecast_time': self.forecast_time,
        }

    def create_alert(self, **overrides):
        return HeatAlert.objects.create(**{**self.alert_data, **overrides})

    def test_valid_alert_normalizes_location_and_persists(self):
        alert = HeatAlert(**self.alert_data)
        alert.full_clean()
        alert.save()

        stored = HeatAlert.objects.get(pk=alert.pk)
        self.assertEqual(stored.city, 'New Delhi')
        self.assertEqual(stored.country, 'India')
        self.assertTrue(stored.is_active)
        self.assertIsNotNone(stored.created_at)
        self.assertIsNotNone(stored.updated_at)

    def test_active_duplicate_forecast_is_rejected_by_database(self):
        self.create_alert()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_alert(risk_level=RiskLevel.EXTREME_DANGER)

    def test_deactivated_alert_allows_replacement_for_same_forecast(self):
        existing = self.create_alert(is_active=False)
        replacement = self.create_alert()

        self.assertFalse(existing.is_active)
        self.assertTrue(replacement.is_active)

    def test_different_forecast_period_can_have_active_alert(self):
        first = self.create_alert()
        second = self.create_alert(
            forecast_time=self.forecast_time + timedelta(hours=1),
        )

        self.assertNotEqual(first.pk, second.pk)

    def test_invalid_location_and_humidity_fail_validation(self):
        for field, value in (
            ('latitude', Decimal('-91')),
            ('longitude', Decimal('181')),
            ('humidity_percent', Decimal('-0.01')),
        ):
            with self.subTest(field=field):
                alert = HeatAlert(**{**self.alert_data, field: value})
                with self.assertRaises(ValidationError):
                    alert.full_clean()


class HeatAlertAdminTests(TestCase):
    def setUp(self):
        self.alert = HeatAlert.objects.create(
            city='New Delhi',
            country='India',
            latitude=Decimal('28.613900'),
            longitude=Decimal('77.209000'),
            temperature_c=Decimal('42.50'),
            humidity_percent=Decimal('55.00'),
            heat_index_c=Decimal('45.25'),
            risk_level=RiskLevel.DANGER,
            message='Dangerous forecast heat stress expected.',
            recommendation='Limit outdoor activity.',
            forecast_time=datetime.now(datetime_timezone.utc)
            + timedelta(hours=6),
        )

    def test_anonymous_user_cannot_access_alert_admin(self):
        response = self.client.get(
            reverse('admin:alerts_heatalert_changelist'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin:login'), response.url)

    def test_staff_without_model_permission_cannot_view_alerts(self):
        user = get_user_model().objects.create_user(
            username='limited-staff',
            password='unused-test-password',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse('admin:alerts_heatalert_changelist'),
        )

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_view_and_deactivate_alerts(self):
        user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.test',
            password='unused-test-password',
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse('admin:alerts_heatalert_changelist'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Deactivate selected forecast alerts')
        self.assertContains(response, 'is_active')

        action_response = self.client.post(
            reverse('admin:alerts_heatalert_changelist'),
            {
                'action': 'deactivate_alerts',
                '_selected_action': [str(self.alert.pk)],
                'index': '0',
            },
            follow=True,
        )

        self.assertEqual(action_response.status_code, 200)
        self.alert.refresh_from_db()
        self.assertFalse(self.alert.is_active)
