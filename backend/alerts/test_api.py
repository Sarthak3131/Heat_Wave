from datetime import datetime, timedelta, timezone as datetime_timezone
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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

    def test_active_alerts_filter_by_risk_level(self):
        alert = self.create_alert('New Delhi')
        response = self.client.get(reverse('alerts:active-list'), {'risk_level': alert.risk_level})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_alert_management_requires_staff_and_allows_status_update(self):
        alert = self.create_alert('New Delhi')
        user_model = get_user_model()
        regular_user = user_model.objects.create_user('regular', password='safe-password')
        staff_user = user_model.objects.create_user('admin', password='safe-password', is_staff=True)
        management_url = reverse('alerts:management-list')

        self.assertEqual(self.client.get(management_url).status_code, 403)
        self.client.force_login(regular_user)
        self.assertEqual(self.client.get(management_url).status_code, 403)
        self.client.force_login(staff_user)
        self.assertEqual(self.client.get(management_url, {'status': 'all'}).status_code, 200)

        response = self.client.patch(
            reverse('alerts:management-detail', args=[alert.pk]),
            {'is_active': False},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_active'])
