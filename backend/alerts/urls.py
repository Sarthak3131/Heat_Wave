from django.urls import path

from .views import ActiveAlertListView

app_name = 'alerts'

urlpatterns = [
    path('', ActiveAlertListView.as_view(), name='active-list'),
]
