from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Lid, Ouder


class CoachLidDownloadResource(resources.ModelResource):
    ouder_1_gsm = fields.Field(
        attribute="moeder",
        column_name="Ouder 1: Gsmnummer",
        widget=ForeignKeyWidget(Ouder, "gsmnummer")
    )
    ouder_2_gsm = fields.Field(
        attribute="vader",
        column_name="Ouder 2: Gsmnummer",
        widget=ForeignKeyWidget(Ouder, "gsmnummer")
    )
    ouder_1_mail = fields.Field(
        attribute="moeder",
        column_name="Ouder 1: Mail",
        widget=ForeignKeyWidget(Ouder, "email")
    )
    ouder_2_mail = fields.Field(
        attribute="vader",
        column_name="Ouder 2: Mail",
        widget=ForeignKeyWidget(Ouder, "email")
    )
    class Meta:
        model = Lid
        fields = (
            "voornaam",
            "familienaam",
            "gsmnummer",
            "email",
            "ouder_1_gsm",
            "ouder_2_gsm",
            "ouder_1_mail",
            "ouder_2_mail",
        )

