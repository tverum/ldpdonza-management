from management.main.betalingen import genereer_betaling
from management.models import (
    Betaling,
    Functie,
    Lid,
    LidgeldKlasse,
    Ploeg,
    PloegLid,
    Seizoen,
)
from management.tests.generic_test_case import GenericBetalingTestCase

TEST_LIDGELD_3MAAL = 360
TEST_LIDGELD_2MAAL = 315
TEST_LIDGELD_STARTERS = 200


class GenerateBetalingTeamSuccessTestCase(GenericBetalingTestCase):
    """
    Testcase to check the successful generation of betalingen.
    To test:
        - Single person, single team. Betaling should contain the correct amount
    """

    def test_single_team_success(self):
        """
        Test the successful generation of Betaling for a single person in a single team.
        """
        # TODO: add logging
        # Add ploeglid to ploeg with specific lidgeldklasse
        klasse = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_3MAAL)
        seizoen = Seizoen.objects.get(pk=1)
        ploeg = Ploeg.objects.get(lidgeldklasse=klasse, seizoen=seizoen)
        lid = Lid.objects.get(pk=1)

        PloegLid.objects.create(
            ploeg=ploeg, lid=lid, functie=Functie.objects.get(functie="Speler")
        )

        # Genereer betaling
        genereer_betaling(lid=lid, seizoen=seizoen)

        # Check that there is only 1 betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 1)

        res_betaling = betalingen[0]
        self.assertEqual(res_betaling.lid, lid)
        self.assertEqual(res_betaling.origineel_bedrag, TEST_LIDGELD_3MAAL)
        self.assertEqual(res_betaling.afgelost_bedrag, 0)
        self.assertEqual(res_betaling.seizoen, seizoen)
        self.assertNotEqual(res_betaling.mededeling, "")

    def test_multiple_teams_success_1(self):
        """
        Test the succesful generation of Betaling for a single person who is in multiple teams.
        """
        # Add the member to the 2 different teams
        klasse_1 = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_3MAAL)
        klasse_2 = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_2MAAL)
        seizoen = Seizoen.objects.get(pk=1)
        ploeg_1 = Ploeg.objects.get(lidgeldklasse=klasse_1, seizoen=seizoen)
        ploeg_2 = Ploeg.objects.get(lidgeldklasse=klasse_2, seizoen=seizoen)
        lid = Lid.objects.get(pk=1)

        PloegLid.objects.create(
            ploeg=ploeg_1,
            lid=lid,
            functie=Functie.objects.get(functie="Speler"),
        )
        PloegLid.objects.create(
            ploeg=ploeg_2,
            lid=lid,
            functie=Functie.objects.get(functie="Speler"),
        )

        # Genereer betaling
        genereer_betaling(lid=lid, seizoen=seizoen)

        # Check that there is only 1 betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 1)

        # Betaling should be for the highest of the 2 bedragen
        res_betaling = betalingen[0]
        self.assertEqual(res_betaling.lid, lid)
        self.assertEqual(res_betaling.origineel_bedrag, TEST_LIDGELD_3MAAL)
        self.assertEqual(res_betaling.afgelost_bedrag, 0)
        self.assertEqual(res_betaling.seizoen, seizoen)
        self.assertNotEqual(res_betaling.mededeling, "")
