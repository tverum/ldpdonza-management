import csv

from django.contrib import admin
from django.http import HttpResponse
from guardian.admin import GuardedModelAdmin

from .models import Lid, Functie, Ouder, Ploeg, PloegLid, Seizoen, LidgeldKlasse, Betaling


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


@admin.register(Betaling)
class BetalingAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("origineel_bedrag", "afgelost_bedrag", "lid", "seizoen", "mails_verstuurd")
    actions = ["export_as_csv"]


@admin.register(Lid)
class LidAdmin(admin.ModelAdmin, ExportCsvMixin):
    search_fields = ('voornaam', 'familienaam')
    actions = ["export_as_csv"]


class PloegAdmin(GuardedModelAdmin):
    pass


admin.site.register(Functie)
admin.site.register(Ouder)
admin.site.register(Ploeg, PloegAdmin)
admin.site.register(PloegLid)
admin.site.register(Seizoen)
admin.site.register(LidgeldKlasse)
