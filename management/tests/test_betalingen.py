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

TEST_LIDGELD_1 = 360


class GenerateBetalingTeamSuccessTestCase(GenericBetalingTestCase):
    """
    Testcase to check the successful generation of betalingen.
    To test:
        - Single person, single team. Betaling should contain the correct amount
    """

    def setUp(self) -> None:
        super().setUp()
        # Select lidgeldklasse with specific amount.
        klasse = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_1)

        # Add ploeglid to ploeg with specific leeftijdsklasse
        seizoen = Seizoen.objects.get(pk=1)
        ploeg = Ploeg.objects.get(lidgeldklasse=klasse, seizoen=seizoen)
        lid = Lid.objects.get(pk=1)
        PloegLid.objects.create(
            ploeg=ploeg, lid=lid, functie=Functie.objects.get(functie="Speler")
        )

    def test_single_team_success(self):
        """
        Test the successful generation of Betaling for a single person in a single team.
        """
        seizoen = Seizoen.objects.get(pk=1)
        lid = Lid.objects.get(pk=1)
        genereer_betaling(lid=lid, seizoen=seizoen)

        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 1)

        res_betaling = betalingen[0]
        self.assertEqual(res_betaling.lid, lid)
        self.assertEqual(res_betaling.origineel_bedrag, TEST_LIDGELD_1)
        self.assertEqual(res_betaling.afgelost_bedrag, 0)
        self.assertEqual(res_betaling.seizoen, seizoen)
        self.assertNotEqual(res_betaling.mededeling, "")
