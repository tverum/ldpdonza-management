from django.core.management.base import BaseCommand

from ...models import *
from ...utils import get_current_seizoen

import pandas as pd
import csv


class Command(BaseCommand):
    help = "Uitzonderlijke fix voor de corona-betalingen"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        filename = options['csv_file']
        _lidgelden = read_lidgeld_csv(filename)
        cleaned_lidgelden = clean(_lidgelden)

        _seizoen = get_current_seizoen(None)

        for _, _lidgeld in cleaned_lidgelden.iterrows():
            _lid = Lid.objects.get(
                club_id=_lidgeld['club id']
            )

            _betaling_filter = Betaling.objects.filter(
                lid=_lid,
                seizoen=_seizoen
            )

            if _betaling_filter.exists():
                continue
            else:
                betaling = Betaling.objects.create(
                    origineel_bedrag=_lidgeld['Lidgeld'],
                    afgelost_bedrag=_lidgeld['Lidgeld'],
                    lid=_lid,
                    seizoen=_seizoen,
                    mededeling="n/a",
                    type="normaal",
                    status="voltooid",
                    mails_verstuurd="",
                    aflossingen=datetime.strftime(datetime.now(), "%d/%m/%Y")
                )
                betaling.save()

        print(len(Betaling.objects.filter(seizoen=_seizoen)))


def read_lidgeld_csv(filename: str) -> pd.DataFrame:
    """
    Read the lidgelden from the csv and return dictionaries
    Args:
        filename: the filename where the lidgelden are stored

    Returns: a list of dictionaries for each row.
    """
    with open(filename) as csvfile:
        lidgeldreader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        _lidgelden = list(lidgeldreader)
        _lidgelden = [{k: v for k, v in row.items() if k} for row in
                      _lidgelden]  # Remove empty keys from lidgelden

        # Construeer pandas.Dataframe voor de lidgelden
        _lidgelden = pd.DataFrame(_lidgelden)
        _lidgelden['club id'] = pd.to_numeric(_lidgelden['club id'])  # Convert club_id to numeric
        _lidgelden['Lidgeld'] = pd.to_numeric(_lidgelden['Lidgeld'])  # Convert Lidgeld to numeric
        return pd.DataFrame(_lidgelden)


def clean(_lidgelden: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the lijst van lidgelden
    Args:
        _lidgelden: De dataframe met lidgelden

    Returns: Een gecleande lijst met lidgelden
    """
    _lidgelden['Lidgeld'] = _lidgelden.groupby(['club id'])['Lidgeld'].transform('max')
    _lidgelden = _lidgelden.drop_duplicates(subset=['club id'])
    _lidgelden = _lidgelden[_lidgelden['Lidgeld'].notna()]
    return _lidgelden
