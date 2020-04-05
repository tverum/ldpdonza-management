from django.urls import path

from . import views

app_name = 'management'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path("leden/", views.LidListView.as_view(), name='leden'),
    path("leden/<int:pk>", views.LidEditView.as_view(), name="lid"),
    path("leden/nieuw", views.LidNewView.as_view(), name='nieuw_lid'),
]