import django_tables2 as tables
from ..models import Lid
from django.urls import reverse


class LidTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor='pk')
    selection = tables.CheckBoxColumn(
        accessor="pk",
        attrs={
            "th__input": {
                "onclick": "toggle(this)"
            }
        },
        orderable=False
    )

    class Meta:
        model = Lid
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "voornaam",
            "familienaam",
            "geboortedatum",
            "familieleden"
        )
        row_attrs = {
            "class": "clickable",
            "data-href": lambda record: reverse('management:lid', kwargs={'pk': record.club_id}),
        }
        attrs = {
            "class": "table table-hover",
        }
