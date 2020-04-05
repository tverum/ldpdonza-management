from django.urls import path

from . import views

app_name = 'management'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path("leden/", views.LidListView.as_view(), name='leden'),
    path("leden/<int:lid_id>", views.LidDetailView.as_view(), name="lid")
]