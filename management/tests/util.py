import random
import string
from typing import List
from management.models import Functie, Lid, LidgeldKlasse, Ploeg, Seizoen
from management.main.utils import generate_uid


TEST_LIDGELD_3MAAL = 360
TEST_LIDGELD_2MAAL = 315
TEST_LIDGELD_STARTERS = 200
TEST_LIDGELD_SENIOREN = 0


def create_basic_teams():
    """
    Create 6 basic teams for testing purposes:
    - Seniors men
    - Seniors women
    - Youth men - 3 practices
    - Youth women - 3 practices
    - Youth mixed - 3 practices
    - Youth men - 2 practices
    - Youth women - 2 practices
    - Youth mixed - 2 practices
    """
    t_seizoen = Seizoen.objects.get(pk=1)  # There's only 1 season

    klasse_senioren = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_SENIOREN)
    klasse_3_maal = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_3MAAL)
    klasse_2_maal = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_2MAAL)

    # Create mannen senioren
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Mannen Senioren",
        korte_naam="MS",
        min_geboortejaar=0,
        max_geboortejaar=2000,
        uitzonderings_geboortejaar=2002,
        geslacht="m",
        lidgeldklasse=klasse_senioren,
    )
    # Create vrouwen senioren
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Vrouwen Senioren",
        korte_naam="VS",
        min_geboortejaar=0,
        max_geboortejaar=2000,
        uitzonderings_geboortejaar=2002,
        geslacht="v",
        lidgeldklasse=klasse_senioren,
    )
    # Create mannen jeugd - 3 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Mannen Jeugd (3 maal)",
        korte_naam="MJ3",
        min_geboortejaar=2001,
        max_geboortejaar=2002,
        uitzonderings_geboortejaar=2004,
        geslacht="m",
        lidgeldklasse=klasse_3_maal,
    )
    # Create vrouwen jeugd - 3 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Vrouwen Jeugd (3 maal)",
        korte_naam="VJ3",
        min_geboortejaar=2001,
        max_geboortejaar=2002,
        uitzonderings_geboortejaar=2004,
        geslacht="v",
        lidgeldklasse=klasse_3_maal,
    )
    # Create gemengd jeugd - 3 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Gemengd Jeugd (3 maal)",
        korte_naam="GJ3",
        min_geboortejaar=2001,
        max_geboortejaar=2002,
        uitzonderings_geboortejaar=2004,
        geslacht="g",
        lidgeldklasse=klasse_3_maal,
    )
    # Create mannen jeugd - 2 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Mannen Jeugd (2 maal)",
        korte_naam="MJ2",
        min_geboortejaar=2001,
        max_geboortejaar=2002,
        uitzonderings_geboortejaar=2004,
        geslacht="m",
        lidgeldklasse=klasse_2_maal,
    )
    # Create vrouwen jeugd - 2 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Vrouwen Jeugd (2 maal)",
        korte_naam="VJ2",
        min_geboortejaar=2001,
        max_geboortejaar=2002,
        uitzonderings_geboortejaar=2004,
        geslacht="v",
        lidgeldklasse=klasse_2_maal,
    )
    # Create gemengd jeugd - 2 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Gemengd Jeugd (2 maal)",
        korte_naam="GJ2",
        min_geboortejaar=2001,
        max_geboortejaar=2002,
        uitzonderings_geboortejaar=2004,
        geslacht="g",
        lidgeldklasse=klasse_2_maal,
    )
    # Create mannen jeugd - 2 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Mannen Jeugd (3 maal) - 2",
        korte_naam="MJ3-2",
        min_geboortejaar=2013,
        max_geboortejaar=2014,
        uitzonderings_geboortejaar=2016,
        geslacht="m",
        lidgeldklasse=klasse_3_maal,
    )
    # Create vrouwen jeugd - 2 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Vrouwen Jeugd (3 maal) - 2",
        korte_naam="VJ3-2",
        min_geboortejaar=2013,
        max_geboortejaar=2014,
        uitzonderings_geboortejaar=2016,
        geslacht="v",
        lidgeldklasse=klasse_3_maal,
    )
    # Create gemengd jeugd - 2 maal
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Gemengd Jeugd (3 maal) - 2",
        korte_naam="GJ3-2",
        min_geboortejaar=2013,
        max_geboortejaar=2014,
        uitzonderings_geboortejaar=2016,
        geslacht="g",
        lidgeldklasse=klasse_3_maal,
    )
    # Create mannen jeugd - 2 maal - jong
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Mannen Jeugd (2 maal) - 2",
        korte_naam="MJ2-2",
        min_geboortejaar=2013,
        max_geboortejaar=2014,
        uitzonderings_geboortejaar=2016,
        geslacht="m",
        lidgeldklasse=klasse_2_maal,
    )
    # Create vrouwen jeugd - 2 maal - jong
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Vrouwen Jeugd (2 maal) - 2",
        korte_naam="VJ2-2",
        min_geboortejaar=2013,
        max_geboortejaar=2014,
        uitzonderings_geboortejaar=2016,
        geslacht="v",
        lidgeldklasse=klasse_2_maal,
    )
    # Create gemengd jeugd - 2 maal - jong
    Ploeg.objects.create(
        seizoen=t_seizoen,
        naam="Gemengd Jeugd (2 maal) - 2",
        korte_naam="GJ2-2",
        min_geboortejaar=2013,
        max_geboortejaar=2014,
        uitzonderings_geboortejaar=2016,
        geslacht="g",
        lidgeldklasse=klasse_2_maal,
    )


def create_lid_personas():
    """
    Create the personas for 4 members:
    - John Doe: Man - 2002
    - Jane Doe: Woman - 2002 (younger sister of John)
    - Emma Smedth: Woman - 2014
    - Paul Smith: Man - 2014
    """
    create_willekeurig_lid(
        voornaam="John",
        familienaam="Doe",
        geslacht="m",
        geboortedatum="2002-01-01",
    )
    create_willekeurig_lid(
        voornaam="Jane",
        familienaam="Doe",
        geslacht="v",
        geboortedatum="2002-10-01",
        familieleden=[Lid.objects.get(voornaam="John", familienaam="Doe")],
    )
    create_willekeurig_lid(
        voornaam="Emma",
        familienaam="Smedt",
        geslacht="v",
        geboortedatum="2014-01-01",
    )
    create_willekeurig_lid(
        voornaam="Paul",
        familienaam="Smith",
        geslacht="m",
        geboortedatum="2014-01-01",
    )


def create_willekeurig_lid(
    voornaam: str,
    familienaam: str,
    geslacht: str,
    geboortedatum: str,
    familieleden: List[Lid] = [],
):
    """
    Scaffolding to quickly be able to create a lid

    Args:
        voornaam (str): lid voornaam
        familienaam (str): lid familienaam
        geslacht (str): lid geslacht: "m" of "v"
        geboortedatum (str): in YYYY-MM-DD format
        familieleden (List[Lid]): familieleden
    """
    lid = Lid.objects.create(
        voornaam=voornaam,
        familienaam=familienaam,
        geslacht=geslacht,
        sportief_lid=True,
        betalend_lid=True,
        actief_lid=True,
        straatnaam_en_huisnummer=get_random_string(10),
        geboortedatum=geboortedatum,
        postcode=random.randint(1, 9999),
        gemeente=get_random_string(10),
        gsmnummer=get_random_string(10),
        uid=generate_uid(),
    )
    lid.functies.set([Functie.objects.get(functie="Speler")])
    lid.familieleden.set(familieleden)
    for fl in familieleden:
        fl.familieleden.add(lid)
        fl.save()
    lid.save()


def get_random_string(length: int) -> str:
    """
    Get a string of random length.
    From https://pynative.com/python-generate-random-string/

    Args:
        length (int): the length of the random string
    """
    # With combination of lower and upper case
    result_str = "".join(
        random.choice(string.ascii_letters) for _ in range(length)
    )
    return result_str
