from datetime import datetime, timedelta, timezone as datetime_timezone
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from weather.models import RiskLevel

from .models import HeatAlert


class ActiveAlertsApiTests(TestCase):
    def create_alert(self, city, *, active=True, hours=1):
        return HeatAlert.objects.create(
            city=city,
            country='India',
            latitude=Decimal('28.600000'),
            longitude=Decimal('77.200000'),
            temperature_c=Decimal('42.00'),
            humidity_percent=Decimal('60.00'),
            heat_index_c=Decimal('45.00'),
            risk_level=RiskLevel.DANGER,
            message='Forecast heat risk.',
            recommendation='Stay cool and hydrated.',
            forecast_time=(
                datetime.now(datetime_timezone.utc) + timedelta(hours=hours)
            ),
            is_active=active,
        )

    def test_lists_active_alerts_only_with_pagination(self):
        self.create_alert('New Delhi', hours=1)
        self.create_alert('New Delhi', active=False, hours=2)
        self.create_alert('Mumbai', hours=3)

        response = self.client.get(
            reverse('alerts:active-list'),
            {'city': 'Delhi', 'page_size': '1'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertTrue(response.json()['results'][0]['is_active'])
        self.assertEqual(response.json()['results'][0]['city'], 'New Delhi')

    def test_rejects_blank_city_filter(self):
        response = self.client.get(
            reverse('alerts:active-list'),
            {'city': '   '},
        )

        self.assertEqual(response.status_code, 400)

    def test_rejects_invalid_page_size(self):
        response = self.client.get(
            reverse('alerts:active-list'),
            {'page_size': '0'},
        )

        self.assertEqual(response.status_code, 400)

    def test_alert_endpoint_does_not_allow_public_writes(self):
        response = self.client.post(
            reverse('alerts:active-list'),
            {'city': 'New Delhi'},
        )

        self.assertEqual(response.status_code, 405)
