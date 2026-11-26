from datetime import datetime, timedelta, timezone as datetime_timezone
from decimal import Decimal

from django.test import TestCase

from weather.models import RiskLevel
from weather.services.open_meteo import InvalidWeatherRequest

from .models import HeatAlert
from .services import generate_forecast_alerts


class ForecastAlertServiceTests(TestCase):
    def setUp(self):
        self.location = {
            'city': ' New Delhi ',
            'country': ' India ',
            'latitude': Decimal('28.613900'),
            'longitude': Decimal('77.209000'),
        }
        self.start = datetime(2026, 6, 1, 12, tzinfo=datetime_timezone.utc)

    def forecast(self, rows, timezone='Etc/UTC'):
        return {
            'timezone': {'name': timezone},
            'hourly': rows,
        }

    def row(self, hour, temperature=42, humidity=55):
        forecast_time = self.start + timedelta(hours=hour)
        return {
            'time': forecast_time.isoformat(),
            'temperature_c': temperature,
            'relative_humidity_percent': humidity,
        }

    def generate(self, forecast):
        return generate_forecast_alerts(
            **self.location,
            forecast=forecast,
        )

    def test_creates_alert_for_danger_and_extreme_danger_forecasts(self):
        result = self.generate(
            self.forecast(
                [
                    self.row(0, temperature=38, humidity=55),
                    self.row(1, temperature=46, humidity=60),
                    self.row(2, temperature=30, humidity=50),
                    self.row(3, temperature=None, humidity=60),
                ]
            )
        )

        alerts = list(HeatAlert.objects.order_by('forecast_time'))
        self.assertEqual(result, {'created': 2, 'updated': 0, 'deactivated': 0})
        self.assertEqual(len(alerts), 2)
        self.assertEqual(alerts[0].city, 'New Delhi')
        self.assertEqual(alerts[0].country, 'India')
        self.assertEqual(alerts[0].risk_level, RiskLevel.DANGER)
        self.assertEqual(alerts[0].forecast_time.utcoffset(), timedelta(0))
        self.assertTrue(alerts[0].message.startswith('Danger heat risk'))
        self.assertTrue(alerts[0].recommendation)
        self.assertEqual(alerts[1].risk_level, RiskLevel.EXTREME_DANGER)

    def test_local_forecast_time_is_interpreted_in_its_iana_timezone(self):
        forecast = self.forecast(
            [
                {
                    'time': '2026-06-01T17:30',
                    'temperature_c': 42,
                    'relative_humidity_percent': 55,
                }
            ],
            timezone='Asia/Kolkata',
        )

        self.generate(forecast)
        alert = HeatAlert.objects.get()
        self.assertEqual(
            alert.forecast_time,
            datetime(2026, 6, 1, 12, tzinfo=datetime_timezone.utc),
        )

    def test_refresh_updates_existing_alert_without_duplicate(self):
        self.generate(self.forecast([self.row(0)]))

        result = self.generate(
            self.forecast([self.row(0, temperature=43, humidity=60)])
        )

        self.assertEqual(result, {'created': 0, 'updated': 1, 'deactivated': 0})
        self.assertEqual(HeatAlert.objects.filter(is_active=True).count(), 1)
        alert = HeatAlert.objects.get(is_active=True)
        self.assertEqual(alert.temperature_c, Decimal('43.00'))
        self.assertEqual(alert.humidity_percent, Decimal('60.00'))

    def test_resolved_forecast_period_deactivates_existing_alert(self):
        self.generate(self.forecast([self.row(0)]))

        result = self.generate(self.forecast([self.row(0, temperature=30)]))

        self.assertEqual(result, {'created': 0, 'updated': 0, 'deactivated': 1})
        self.assertFalse(HeatAlert.objects.get().is_active)

    def test_unreturned_forecast_period_is_not_deactivated(self):
        self.generate(self.forecast([self.row(0), self.row(1)]))

        result = self.generate(self.forecast([self.row(0, temperature=30)]))

        self.assertEqual(result['deactivated'], 1)
        self.assertTrue(
            HeatAlert.objects.get(forecast_time=self.start + timedelta(hours=1)).is_active
        )

    def test_missing_measurements_do_not_deactivate_existing_alert(self):
        self.generate(self.forecast([self.row(0)]))

        result = self.generate(
            self.forecast([self.row(0, temperature=None, humidity=55)])
        )

        self.assertEqual(result, {'created': 0, 'updated': 0, 'deactivated': 0})
        self.assertTrue(HeatAlert.objects.get().is_active)

    def test_inactive_alert_can_be_replaced_by_a_new_active_forecast(self):
        self.generate(self.forecast([self.row(0)]))
        HeatAlert.objects.update(is_active=False)

        result = self.generate(self.forecast([self.row(0)]))

        self.assertEqual(result, {'created': 1, 'updated': 0, 'deactivated': 0})
        self.assertEqual(HeatAlert.objects.count(), 2)
        self.assertEqual(HeatAlert.objects.filter(is_active=True).count(), 1)

    def test_invalid_location_timezone_and_hourly_data_are_rejected(self):
        invalid_cases = (
            ({**self.location, 'city': '  '}, self.forecast([self.row(0)])),
            ({**self.location, 'latitude': Decimal('91')}, self.forecast([self.row(0)])),
            ({**self.location, 'longitude': Decimal('-181')}, self.forecast([self.row(0)])),
            (self.location, self.forecast([self.row(0)], timezone='not/a-zone')),
            (self.location, {'timezone': {'name': 'Etc/UTC'}, 'hourly': None}),
            (
                self.location,
                self.forecast([{'time': 'invalid', 'temperature_c': 42}]),
            ),
        )
        for location, forecast in invalid_cases:
            with self.subTest(location=location, forecast=forecast):
                with self.assertRaises(InvalidWeatherRequest):
                    generate_forecast_alerts(**location, forecast=forecast)
        self.assertEqual(HeatAlert.objects.count(), 0)
