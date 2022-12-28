import logging

from django.core.exceptions import ValidationError
from django.test import tag

from management.tests.generic_test_case import GenericPloegLidTestCase
from management.models import Functie, Lid, Ploeg, PloegLid
from management.tests.util import create_basic_teams, create_lid_personas

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

    def setUp(self) -> None:
        """
        Setup function.
        Create the scaffolding to run the test.
        """
        create_basic_teams()
        create_lid_personas()
        return super().setUp()

    @tag("ploeglid")
    def test_ploeglid_succesful(self):
        """
        Test the succesful creation of ploeglid relaties
        """
        gemengd_jeugd_oud = Ploeg.objects.get(korte_naam="GJ3")
        mannen_jeugd_oud = Ploeg.objects.get(korte_naam="MJ3")
        vrouwen_jeugd_oud = Ploeg.objects.get(korte_naam="VJ3")
        gemengd_jeugd_jong = Ploeg.objects.get(korte_naam="GJ3-2")
        mannen_jeugd_jong = Ploeg.objects.get(korte_naam="MJ3-2")
        vrouwen_jeugd_jong = Ploeg.objects.get(korte_naam="VJ3-2")
        mannen_senioren = Ploeg.objects.get(korte_naam="MS")
        vrouwen_senioren = Ploeg.objects.get(korte_naam="VS")

        john = Lid.objects.get(voornaam="John", familienaam="Doe")
        jane = Lid.objects.get(voornaam="Jane", familienaam="Doe")
        emma = Lid.objects.get(voornaam="Emma", familienaam="Smedt")
        paul = Lid.objects.get(voornaam="Paul", familienaam="Smith")

        speler = Functie.objects.get(functie="Speler")

        try:
            PloegLid.objects.create(
                ploeg=mannen_jeugd_oud, lid=john, functie=speler
            )
            PloegLid.objects.create(
                ploeg=vrouwen_jeugd_oud, lid=jane, functie=speler
            )
            PloegLid.objects.create(
                ploeg=gemengd_jeugd_oud, lid=john, functie=speler
            )
            PloegLid.objects.create(
                ploeg=gemengd_jeugd_oud, lid=jane, functie=speler
            )
            PloegLid.objects.create(
                ploeg=mannen_senioren, lid=john, functie=speler
            )
            PloegLid.objects.create(
                ploeg=vrouwen_senioren, lid=jane, functie=speler
            )
            PloegLid.objects.create(
                ploeg=mannen_jeugd_jong, lid=paul, functie=speler
            )
            PloegLid.objects.create(
                ploeg=vrouwen_jeugd_jong, lid=emma, functie=speler
            )
            PloegLid.objects.create(
                ploeg=gemengd_jeugd_jong, lid=paul, functie=speler
            )
            PloegLid.objects.create(
                ploeg=gemengd_jeugd_jong, lid=emma, functie=speler
            )
        except ValidationError:
            self.fail(
                "Validation Error bij het toewijzen van correcte PloegLid relaties"
            )

    @tag("ploeglid")
    def test_ploeglid_geslacht(self):
        """
        Test dat een lid van een bepaald geslacht niet in een ploeg van het andere geslacht kan terechtkomen.
        """
        mannen_jeugd_oud = Ploeg.objects.get(korte_naam="MJ3")
        vrouwen_jeugd_oud = Ploeg.objects.get(korte_naam="VJ3")
        mannen_jeugd_jong = Ploeg.objects.get(korte_naam="MJ3-2")
        vrouwen_jeugd_jong = Ploeg.objects.get(korte_naam="VJ3-2")
        mannen_senioren = Ploeg.objects.get(korte_naam="MS")
        vrouwen_senioren = Ploeg.objects.get(korte_naam="VS")

        john = Lid.objects.get(voornaam="John", familienaam="Doe")
        jane = Lid.objects.get(voornaam="Jane", familienaam="Doe")
        emma = Lid.objects.get(voornaam="Emma", familienaam="Smedt")
        paul = Lid.objects.get(voornaam="Paul", familienaam="Smith")

        speler = Functie.objects.get(functie="Speler")

        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=vrouwen_senioren, lid=john, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=mannen_jeugd_oud, lid=jane, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=mannen_senioren, lid=jane, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=vrouwen_jeugd_oud, lid=john, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=mannen_jeugd_jong, lid=emma, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=vrouwen_jeugd_jong, lid=paul, functie=speler
            )

    @tag("ploeglid")
    def test_ploeglid_leeftijd(self):
        """
        Test dat een ploeglid van een bepaalde leeftijd niet in een ploeg kan terechtkomen die niet voor zijn leeftijd is.
        """
        gemengd_jeugd_oud = Ploeg.objects.get(korte_naam="GJ3")
        mannen_jeugd_oud = Ploeg.objects.get(korte_naam="MJ3")
        vrouwen_jeugd_oud = Ploeg.objects.get(korte_naam="VJ3")
        gemengd_jeugd_jong = Ploeg.objects.get(korte_naam="GJ3-2")
        mannen_jeugd_jong = Ploeg.objects.get(korte_naam="MJ3-2")
        vrouwen_jeugd_jong = Ploeg.objects.get(korte_naam="VJ3-2")
        mannen_senioren = Ploeg.objects.get(korte_naam="MS")
        vrouwen_senioren = Ploeg.objects.get(korte_naam="VS")

        john = Lid.objects.get(voornaam="John", familienaam="Doe")
        jane = Lid.objects.get(voornaam="Jane", familienaam="Doe")
        emma = Lid.objects.get(voornaam="Emma", familienaam="Smedt")
        paul = Lid.objects.get(voornaam="Paul", familienaam="Smith")

        speler = Functie.objects.get(functie="Speler")

        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=mannen_jeugd_jong, lid=john, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=vrouwen_jeugd_jong, lid=jane, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=gemengd_jeugd_jong, lid=john, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=gemengd_jeugd_jong, lid=jane, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=mannen_jeugd_oud, lid=paul, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=vrouwen_jeugd_oud, lid=emma, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=gemengd_jeugd_oud, lid=emma, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=gemengd_jeugd_oud, lid=emma, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=mannen_senioren, lid=paul, functie=speler
            )
        with self.assertRaises(ValidationError):
            PloegLid.objects.create(
                ploeg=vrouwen_senioren, lid=emma, functie=speler
            )

    # TODO: add functie
