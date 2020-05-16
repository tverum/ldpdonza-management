from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Lid, Functie, Ouder, Ploeg, PloegLid, Seizoen, LidgeldKlasse


class PloegAdmin(GuardedModelAdmin):
    pass


admin.site.register(Lid)
admin.site.register(Functie)
admin.site.register(Ouder)
admin.site.register(Ploeg, PloegAdmin)
admin.site.register(PloegLid)
admin.site.register(Seizoen)
admin.site.register(LidgeldKlasse)
