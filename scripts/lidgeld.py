import csv
import pandas as pd


def read_lidgeld_csv(
    filename: str,
) -> pd.DataFrame:
    """
    Read the lidgelden from the csv and return dictionaries
    Args:
        filename: the filename where the lidgelden are stored

    Returns: a list of dictionaries for each row.
    """
    with open(filename) as csvfile:
        lidgeldreader = csv.DictReader(
            csvfile,
            delimiter=";",
            quotechar='"',
        )
        _lidgelden = list(lidgeldreader)
        _lidgelden = [
            {k: v for k, v in row.items() if k} for row in _lidgelden
        ]  # Remove empty keys from lidgelden

        # Construeer pandas.Dataframe voor de lidgelden
        _lidgelden = pd.DataFrame(_lidgelden)
        _lidgelden["club id"] = pd.to_numeric(
            _lidgelden["club id"]
        )  # Convert club_id to numeric
        _lidgelden["Lidgeld"] = pd.to_numeric(
            _lidgelden["Lidgeld"]
        )  # Convert Lidgeld to numeric
        return pd.DataFrame(_lidgelden)


def inspect_values(
    _lidgelden: pd.DataFrame,
) -> None:
    """
    Do data exploration on the lidgelden
    Args:
        _lidgelden: the lidgelden to be inspected

    Returns: None. This function prints out information to the terminal
    """
    print(_lidgelden.keys())  # Alle kolommen
    print(
        _lidgelden[_lidgelden["Lidgeld"].notna()][
            [
                "voornaam",
                "familienaam",
                "Lidgeld",
                "sponsor",
            ]
        ]
    )
    # print(_lidgelden.Ploeg.unique())  # Alle ploegen
    # print(_lidgelden['club id'].nunique())
    # print(_lidgelden[_lidgelden.duplicated(
    #    subset=['club id'],
    #    keep=False
    # )].sort_values('club id')[[
    #    'voornaam',
    #    'familienaam'
    # ]])  # Duplicate club ids
    # print(_lidgelden['Lidgeld'].unique())


def construct_betalingen(
    _lidgelden: pd.DataFrame,
) -> None:
    """
    Construeer betalingen obv. de lijst met lidgelden
    Args:
        _lidgelden: De dataframe met lidgelden

    Returns: Een lijst met Betalingen (zijn nog niet opgeslagen in de database)
    """
    _lidgelden["Lidgeld"] = _lidgelden.groupby(["club id"])[
        "Lidgeld"
    ].transform("max")
    _lidgelden = _lidgelden.drop_duplicates(subset=["club id"])
    _lidgelden = _lidgelden[_lidgelden["Lidgeld"].notna()]
    print(
        _lidgelden[
            [
                "club id",
                "voornaam",
                "familienaam",
                "Lidgeld",
            ]
        ]
    )
    return None


if __name__ == "__main__":
    lidgelden = read_lidgeld_csv("media/lidgeld2021.csv")
    inspect_values(lidgelden)
    # construct_betalingen(lidgelden)
