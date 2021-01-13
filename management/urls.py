from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
                  path("leden/", views.LidTableView.as_view(), name='leden'),
                  path("leden/<int:pk>/", views.LidEditView.as_view(), name="lid"),
                  path("leden/<int:pk>/verwijder", views.verwijder_lid, name="verwijder_lid"),
                  path('lid_modal/<int:pk>/', views.LidModalView.as_view(), name='lid_modal'),
                  path("leden/verwerk/", views.verwerk_leden, name="verwerk_leden"),
                  path("leden/nieuw/", views.LidNewView.as_view(), name='nieuw_lid'),
                  path("ouder/new/", views.create_ouder, name="new_ouder"),
                  path("ploegen/", views.PloegListView.as_view(), name='ploegen'),
                  path("ploegen/new/", views.create_ploeg, name="new_ploeg"),
                  path("ploegen/export_preview/", views.export_ploeg_preview, name="exporteer_ploeg_preview"),
                  path("ploegen/export", views.exporteer_ploegen, name="exporteer_ploegen"),
                  path("ploegen/<int:pk>/select/", views.PloegSelectView.as_view(), name='ploeg_select'),
                  path("ploegen/<int:pk>/view/", views.PloegView.as_view(), name='ploeg_view'),
                  path("ploegen/<int:pk>/export-csv/", views.export_ploeg_csv, name='ploeg_export_csv'),
                  path("ploegen/<int:pk>/export-xlsx/", views.export_ploeg_xlsx, name='ploeg_export_xlsx'),
                  path("betalingen/stuur_mail/<int:pk>/", views.stuur_mail, name="betalingen_mail"),
                  path("betalingen/her_mail/<int:pk>/", views.herinnering_mail, name="herinnering_mail"),
                  path("betalingen/bevestiging/<int:pk>/", views.bevestig_mail, name="bevestig_mail"),
                  path("betalingen/", views.BetalingTableView.as_view(), name="betalingen"),
                  path("change_seizoen/<int:pk>/", views.change_seizoen, name="change_seizoen"),
                  path('', views.IndexView.as_view(), name='index'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
app_name = 'management'

handler500 = views.handler500
