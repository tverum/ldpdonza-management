import django_tables2 as tables
from django.urls import reverse

from ..models import Lid


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
    voornaam = tables.Column(attrs={
        "td": {
            "class": "clickable",
            "data-href": lambda record: reverse('management:lid', kwargs={'pk': record.club_id}),
        }
    })
    familienaam = tables.Column(attrs={
        "td": {
            "class": "clickable",
            "data-href": lambda record: reverse('management:lid', kwargs={'pk': record.club_id}),
        }
    })
    geboortedatum = tables.Column(attrs={
        "td": {
            "class": "clickable",
            "data-href": lambda record: reverse('management:lid', kwargs={'pk': record.club_id}),
        }
    })

    class Meta:
        model = Lid
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "voornaam",
            "familienaam",
            "geboortedatum",
            "familieleden"
        )
        # row_attrs = {
        #    "class": "clickable",
        #    "data-href": lambda record: reverse('management:lid', kwargs={'pk': record.club_id}),
        #}
        attrs = {
            "class": "table table-hover",
        }
