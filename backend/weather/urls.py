from django.urls import path

from .views import (
    CitySearchView,
    CurrentWeatherView,
    ForecastView,
    WeatherHistoryView,
)

app_name = 'weather'

urlpatterns = [
    path('cities/', CitySearchView.as_view(), name='city-search'),
    path('current/', CurrentWeatherView.as_view(), name='current'),
    path('forecast/', ForecastView.as_view(), name='forecast'),
    path('history/', WeatherHistoryView.as_view(), name='history'),
]
