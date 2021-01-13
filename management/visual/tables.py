from datetime import datetime

import django_tables2 as tables
from django.urls import reverse
from django_tables2.utils import A  # alias for Accessor

from ..models import Lid, Betaling, Ploeg


class LidTable(tables.Table):
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
        attrs = {
            "class": "table table-hover",
        }


class PloegTable(tables.Table):
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs={
            "th__input": {
                "onclick": "toggle(this)"
            }
        },
        orderable=False
    )
    bekijk = tables.TemplateColumn(
        template_code="""
        <i class="fas fa-eye" style="width: 16px;"></i>
        """,
        attrs={
            "td": {
                "class": "clickable",
                "data-href": lambda record: reverse('management:ploeg_view', args=[record.ploeg_id]),
            },
        }
    )
    edit = tables.TemplateColumn(
        template_code="""
        <i class="fas fa-pencil-alt" style="width: 16px;"></i>
        """,
        attrs={
            "td": {
                "class": "clickable",
                "data-href": lambda record: reverse('management:ploeg_select', args=[record.ploeg_id]),
            }
        }
    )

    class Meta:
        model = Ploeg
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "naam",
            "bekijk",
            "edit",
            "selection"
        )


class DraftTable(tables.Table):
    title = "Betalingsontwerpen"
    table_pagination = {
        "per_page": 20
    }
    mail_column = tables.LinkColumn("management:betalingen_mail",
                                    text="MAIL",
                                    args=[A("pk")],
                                    attrs={
                                        "a": {
                                            "class": "btn btn-sm btn-success",
                                        }
                                    })

    class Meta:
        model = Betaling
        fields = (
            "lid",
            "origineel_bedrag",
            "mededeling",
            "type"
        )
        attrs = {
            "class": "table table-hover table-sm",
            "td": {
                "class": "text-center",
            },
            "th": {
                "class": "text-center",
            },
        }


class VerstuurdTable(tables.Table):
    title = "Verstuurd"
    table_pagination = {
        "per_page": 30
    }
    mail_column = tables.LinkColumn("management:herinnering_mail",
                                    text="HERINNERING",
                                    args=[A("pk")],
                                    attrs={
                                        "a": {
                                            "class": "btn btn-sm btn-warning",
                                        }
                                    })

    class Meta:
        model = Betaling
        fields = (
            "lid",
            "origineel_bedrag",
            "afgelost_bedrag",
            "mededeling",
            "type",
            "mails_verstuurd",
        )
        row_attrs = {
            "class": lambda record: overdue(record)
        }
        attrs = {
            "class": "table table-hover table-sm",
            "id": "mail-verstuurd",
            "td": {
                "class": "text-center",
            },
            "th": {
                "class": "text-center",
            },
        }


class BetaaldTable(tables.Table):
    title = "Betaald"
    table_pagination = {
        "per_page": 30
    }
    bevestiging_column = tables.LinkColumn("management:bevestig_mail",
                                           text="Bevestiging",
                                           args=[A("pk")],
                                           attrs={
                                               "a": {
                                                   "class": "btn btn-sm btn-success",
                                               }
                                           })

    class Meta:
        model = Betaling
        fields = (
            "lid",
            "origineel_bedrag",
            "type",
        )
        attrs = {
            "class": "table table-hover table-sm",
            "id": "mail-verstuurd",
            "td": {
                "class": "text-center",
            },
            "th": {
                "class": "text-center",
            },
        }


def overdue(record):
    # Calculate the difference between the date of the last mail and the current time
    mail = record.mails_verstuurd.split(";")[-1]
    datum_mail = datetime.strptime(mail, "%Y-%m-%d")
    now = datetime.now()
    delta = now - datum_mail

    # If difference larger than 40 days, payment is overdue
    if delta.days > 40 and record.afgelost_bedrag == 0.0 and record.type == "normaal":
        return "table-danger"
    else:
        return None
