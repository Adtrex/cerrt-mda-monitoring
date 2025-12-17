from django.urls import path
from . import views

urlpatterns = [
    path('', views.scan_page, name='scan_page'),
    path('run-scan/', views.scan_api, name='run_scan'),
    path('download-report/', views.download_report, name='download_report'),
    path("download-docx/", views.download_report_docx, name="download_report_docx"),
]
