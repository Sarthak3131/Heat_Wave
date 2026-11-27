from django.urls import path

from .views import (
    ActiveAlertListView,
    AlertManagementDetailView,
    AlertManagementListView,
)

app_name = 'alerts'

urlpatterns = [
    path('', ActiveAlertListView.as_view(), name='active-list'),
    path('management/', AlertManagementListView.as_view(), name='management-list'),
    path('management/<int:alert_id>/', AlertManagementDetailView.as_view(), name='management-detail'),
]
