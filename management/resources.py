from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from openpyxl import Workbook
from openpyxl.styles import Font

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


def create_workbook(queryset_coaches, queryset_spelers, queryset_pvn):
    workbook = Workbook()

    # Get active worksheet/tab
    worksheet = workbook.active

    columns = [
        "Voornaam",
        "Familienaam",
        "Gsmnummer",
        "Email",
        "GSM Ouder 1",
        "Email Ouder 1",
        "GSM Ouder 2",
        "Email Ouder 2"
    ]

    # --- SPELERS ---
    worksheet.title = 'Spelers'

    cell = worksheet.cell(row=2, column=2)
    cell.value = "SPELERS"
    cell.font = Font(name='Calibri', bold=True, size=20)
    row_num = 4

    # Assign the titles for each cell of the header
    for col_num, column_title in enumerate(columns, 2):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
    # Iterate through all movies
    for lid in queryset_spelers:
        row_num += 1

        # Define the data for each cell in the row
        row = [
            lid.voornaam,
            lid.familienaam,
            str(lid.gsmnummer),
            lid.email,
        ]

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

    # --- COACHES ---
    worksheet = workbook.create_sheet(
        title="Coaches",
        index=1,
    )
    row_num = 2
    cell = worksheet.cell(row=row_num, column=2)
    cell.value = "COACHES"
    cell.font = Font(name='Calibri', bold=True, size=20)
    row_num += 1
    for coach in queryset_coaches:
        row_num += 1

        # Define the data for each cell in the row
        row = [
            coach.voornaam,
            coach.familienaam,
            str(coach.gsmnummer),
            coach.email,
        ]

        # Assign the data for each cell of the row
        for col_num, cell_value in enumerate(row, 2):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    # --- PLOEGVERANTWOORDELIJKEN ---
    worksheet = workbook.create_sheet(
        title="Ploegverantwoordelijken",
        index=1,
    )
    row_num = 2
    cell = worksheet.cell(row=row_num, column=2)
    cell.value = "PLOEGVERANTWOORDELIJKEN"
    cell.font = Font(name='Calibri', bold=True, size=20)
    row_num += 1
    for pv in queryset_pvn:
        row_num += 1

        # Define the data for each cell in the row
        row = [
            pv.voornaam,
            pv.familienaam,
            str(pv.gsmnummer),
            pv.email,
        ]

        # Assign the data for each cell of the row
        for col_num, cell_value in enumerate(row, 2):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
    return workbook
