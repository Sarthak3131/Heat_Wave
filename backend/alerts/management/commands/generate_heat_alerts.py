from django.core.management.base import BaseCommand

from weather.services.open_meteo import OpenMeteoClient

from alerts.services import generate_forecast_alerts


class Command(BaseCommand):
    help = 'Generate or refresh severe forecast heat alerts for one location.'

    def add_arguments(self, parser):
        parser.add_argument('--city', required=True)
        parser.add_argument('--latitude', required=True, type=float)
        parser.add_argument('--longitude', required=True, type=float)
        parser.add_argument('--country', default='')
        parser.add_argument('--days', type=int, default=5)

    def handle(self, *args, **options):
        client = OpenMeteoClient()
        forecast = client.get_forecast(
            options['latitude'],
            options['longitude'],
            days=options['days'],
        )
        result = generate_forecast_alerts(
            city=options['city'],
            country=options['country'],
            latitude=forecast['latitude'],
            longitude=forecast['longitude'],
            forecast=forecast,
        )
        self.stdout.write(
            self.style.SUCCESS(
                'Forecast alerts refreshed: '
                f"{result['created']} created, "
                f"{result['updated']} updated, "
                f"{result['deactivated']} deactivated."
            )
        )
