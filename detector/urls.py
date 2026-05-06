from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("history/", views.history_page, name="history"),
    path("analytics/", views.analytics_page, name="analytics"),
    path("result/<int:record_id>/", views.result_page, name="result"),
    path("api/detect/", views.detect_api, name="detect_api"),
    path("api/history/", views.history_api, name="history_api"),
    path("api/analytics/live/", views.analytics_live_api, name="analytics_live_api"),
    path("api/analytics/chart/", views.analytics_chart_api, name="analytics_chart_api"),
    path("api/result/<int:record_id>/", views.result_api, name="result_api"),
    path("api/export/csv/", views.export_csv_api, name="export_csv_api"),
]
