from django.urls import path
from . import views

app_name = 'report_api'

urlpatterns = [
    path("report", views.ReportView.as_view(), name="report"),
    path("customer-report/<int:pk>", views.CustomerReportView.as_view(), name="customer-report")
]