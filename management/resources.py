from collections import Sequence
from pprint import pprint

from django.db.models import Field
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from openpyxl import Workbook
from openpyxl.styles import Font

from .models import Lid, Ouder, Functie, PloegLid, Ploeg

# A mapping of the string representation of Lid to the actual field.
# No better reverse determination of fields was found so bit of a hack
LID_FIELDS = dict(zip(
    [str(field) for field in Lid._meta.get_fields() if not field.is_relation],
    [field for field in Lid._meta.get_fields() if not field.is_relation]
))


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


def create_team_workbook(queryset_coaches, queryset_spelers, queryset_pvn):
    workbook = Workbook()

    # --- SPELERS ---
    # Get active worksheet/tab
    columns = [
        "Voornaam", "Familienaam", "Gsmnummer", "Email",
        "GSM Ouder 1", "Email Ouder 1", "GSM Ouder 2", "Email Ouder 2"
    ]
    worksheet = workbook.active
    worksheet.title = 'Spelers'

    cell = worksheet.cell(row=2, column=2)
    cell.value = "SPELERS"
    cell.font = Font(name='Calibri', bold=True, size=20)
    row_num = 4

    create_team_sheet(columns, queryset_spelers, row_num, worksheet)

    # --- COACHES ---
    # Create new worksheet
    columns = [
        "Voornaam", "Familienaam", "Gsmnummer", "Email"
    ]
    worksheet = workbook.create_sheet(
        title="Coaches",
        index=1,
    )

    cell = worksheet.cell(row=2, column=2)
    cell.value = "COACHES"
    cell.font = Font(name='Calibri', bold=True, size=20)
    row_num = 4

    create_team_sheet(columns, queryset_coaches, row_num, worksheet)

    # --- PLOEGVERANTWOORDELIJKEN ---
    columns = [
        "Voornaam", "Familienaam", "Gsmnummer", "Email"
    ]
    worksheet = workbook.create_sheet(
        title="Ploegverantwoordelijken",
        index=1,
    )

    cell = worksheet.cell(row=2, column=2)
    cell.value = "PLOEGVERANTWOORDELIJKEN"
    cell.font = Font(name='Calibri', bold=True, size=20)
    row_num = 4

    create_team_sheet(columns, queryset_pvn, row_num, worksheet)

    return workbook


def create_team_sheet(columns, queryset, row_num, worksheet, minimal):
    """
    Create a sheet with a specific queryset
    :param columns: the column names
    :param queryset: the queryset to put into the excel sheet
    :param row_num: the row number to start from
    :param worksheet: the worksheet to write the data to
    :param minimal: minimal data writing (for coaches and pv)
    """
    # Assign the titles for each cell of the header
    for col_num, column_title in enumerate(columns, 2):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
    # Iterate through all movies
    for lid in queryset:
        row_num += 1

        # Define the data for each cell in the row
        row = [
            lid.voornaam,
            lid.familienaam,
            str(lid.gsmnummer),
            lid.email,
        ]

        if not minimal:
            if lid.moeder:
                row.append(str(lid.moeder.gsmnummer))
                row.append(lid.moeder.email)
            else:
                row.append("")
                row.append("")

            if lid.vader:
                row.append(str(lid.vader.gsmnummer))
                row.append(lid.vader.email)
            else:
                row.append("")
                row.append("")

        # Assign the data for each cell of the row
        for col_num, cell_value in enumerate(row, 2):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value


def create_general_workbook(ploegen, selected_fields):
    workbook = Workbook()

    selected_fields = [LID_FIELDS[field] for field in selected_fields]

    # Get active worksheet/tab
    worksheet = workbook.active

    # --- SPELERS ---
    worksheet.title = 'Spelers'

    create_sheet(ploegen, selected_fields, worksheet, Functie.objects.get(functie="Speler"))

    # --- COACHES ---
    worksheet = workbook.create_sheet(
        title="Coaches",
        index=1,
    )
    create_sheet(ploegen, selected_fields, worksheet, Functie.objects.get(functie="Coach"))

    # --- PLOEGVERANTWOORDELIJKEN ---
    worksheet = workbook.create_sheet(
        title="Ploegverantwoordelijken",
        index=1,
    )
    create_sheet(ploegen, selected_fields, worksheet, Functie.objects.get(functie="Ploegverantwoordelijke"))
    return workbook


def create_sheet(ploegen, selected_fields, worksheet, functie: Functie):
    """
    Create a sheet for the specific function
    :param ploegen: the ploegen for which the exported xlsx should be generated
    :param selected_fields: the fields that should be shown
    :param worksheet:
    :param functie:
    :return:
    """
    cell = worksheet.cell(row=2, column=2)
    cell.value = functie.functie
    cell.font = Font(name='Calibri', bold=True, size=20)
    row_num = 4
    # Assign the titles for each cell of the header
    cell = worksheet.cell(row=row_num, column=1)
    cell.value = "Ploeg"
    for col_num, field in enumerate(selected_fields, 2):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = field.verbose_name
    for ploeg in ploegen:
        ploegleden = PloegLid.objects.filter(ploeg=ploeg, functie=functie)
        lid_ids = [ploeglid.lid.club_id for ploeglid in ploegleden]
        queryset_spelers = Lid.objects.filter(club_id__in=lid_ids)

        for lid in queryset_spelers:
            row_num += 1

            row = [str(getattr(lid, field.name)) if getattr(lid, field.name) is not None else '' for field in
                   selected_fields]

            # Assign the data for each cell of the row
            cell = worksheet.cell(row=row_num, column=1)
            cell.value = ploeg.naam

            for col_num, cell_value in enumerate(row, 2):
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.value = cell_value
