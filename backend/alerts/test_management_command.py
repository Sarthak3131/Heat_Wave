from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


class GenerateHeatAlertsCommandTests(SimpleTestCase):
    @patch(
        'alerts.management.commands.generate_heat_alerts.generate_forecast_alerts'
    )
    @patch(
        'alerts.management.commands.generate_heat_alerts.OpenMeteoClient'
    )
    def test_command_fetches_forecast_and_reports_generation_counts(
        self,
        client_class,
        generate_alerts,
    ):
        forecast = {'latitude': 28.6, 'longitude': 77.2, 'hourly': []}
        client_class.return_value.get_forecast.return_value = forecast
        generate_alerts.return_value = {
            'created': 2,
            'updated': 1,
            'deactivated': 3,
        }
        output = StringIO()

        call_command(
            'generate_heat_alerts',
            city='New Delhi',
            country='India',
            latitude=28.6,
            longitude=77.2,
            days=3,
            stdout=output,
        )

        client_class.return_value.get_forecast.assert_called_once_with(
            28.6,
            77.2,
            days=3,
        )
        generate_alerts.assert_called_once_with(
            city='New Delhi',
            country='India',
            latitude=28.6,
            longitude=77.2,
            forecast=forecast,
        )
        self.assertIn('2 created, 1 updated, 3 deactivated', output.getvalue())
