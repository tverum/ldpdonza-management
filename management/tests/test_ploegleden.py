import logging

from django.core.exceptions import ValidationError

from management.tests.generic_test_case import GenericPloegLidTestCase
from management.models import Functie, Lid, Ploeg, PloegLid

logger = logging.getLogger(__name__)


class PloegLidTestCase(GenericPloegLidTestCase):
    """
    Testcase to check that only correct PloegLid-relations can be created.
    This is a proxy to make sure that members of the club can only end up in teams that are suited for them.
    For this we take into account:
    - Age
    - Gender
    - Functie
    """

    def test_ploeglid_geslacht(self):
        """
        Test dat een lid van een bepaald geslacht niet in een ploeg van het andere geslacht kan terechtkomen.
        Mannen: John Doe, Paul Smith
        Vrouwen: Jane Doe, Emma Smedt

        Mannenploegen: 2, 4
        Vrouwenploegen: 3, 5
        """
        gemengd_jeugd = Ploeg.objects.get(pk=1)
        mannen_jeugd = Ploeg.objects.get(pk=2)
        vrouwen_jeugd = Ploeg.objects.get(pk=3)
        mannen_senioren = Ploeg.objects.get(pk=4)
        vrouwen_senioren = Ploeg.objects.get(pk=5)

        john = Lid.objects.get(pk=1)
        jane = Lid.objects.get(pk=2)
        emma = Lid.objects.get(pk=3)
        paul = Lid.objects.get(pk=4)

        speler = Functie.objects.get(functie="Speler")

        try:
            PloegLid.objects.create(
                ploeg=mannen_jeugd, lid=john, functie=speler
            )
            PloegLid.objects.create(
                ploeg=vrouwen_jeugd, lid=jane, functie=speler
            )
            PloegLid.objects.create(
                ploeg=mannen_senioren, lid=john, functie=speler
            )
            PloegLid.objects.create(
                ploeg=vrouwen_senioren, lid=jane, functie=speler
            )
            PloegLid.objects.create(
                ploeg=gemengd_jeugd, lid=emma, functie=speler
            )
            PloegLid.objects.create(
                ploeg=gemengd_jeugd, lid=paul, functie=speler
            )
        except ValidationError:
            self.fail(
                "Validation Error bij het toewijzen van correcte PloegLid relaties"
            )

        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=vrouwen_senioren, lid=john, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=mannen_jeugd, lid=jane, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=mannen_senioren, lid=jane, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=vrouwen_jeugd, lid=john, functie=speler
            )
