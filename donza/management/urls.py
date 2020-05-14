from django.urls import path

from . import views

app_name = 'management'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path("leden/", views.LidTableView.as_view(), name='leden'),
    path("leden/<int:pk>", views.LidEditView.as_view(), name="lid"),
    path("leden/nieuw", views.LidNewView.as_view(), name='nieuw_lid'),
    path("ouder/new", views.create_ouder, name="new_ouder"),
    path("ploegen/", views.PloegListView.as_view(), name='ploegen'),
    path("ploegen/new", views.create_ploeg, name="new_ploeg"),
    path("ploegen/<int:pk>/select", views.PloegSelectView.as_view(), name='ploeg_select'),
    path("ploegen/<int:pk>/view", views.PloegView.as_view(), name='ploeg_view'),
    path("betalingen/genereer", views.genereer, name="betalingen_genereer"),
    # path("betalingen", views.LidTableView.as_view(), name="lidbetalingen"),
]