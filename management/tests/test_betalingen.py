import logging

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

logger = logging.getLogger(__name__)

TEST_LIDGELD_3MAAL = 360
TEST_LIDGELD_2MAAL = 315
TEST_LIDGELD_STARTERS = 200
TEST_LIDGELD_SENIOREN = 0


class GenerateBetalingTestCase(GenericBetalingTestCase):
    """
    Testcase to check the successful generation of betalingen.
    To test:
        - Single person, no team. There should be no betaling generated
        - Single person, single team (youth team). Betaling should contain the correct amount
        - Single person, single team (senior team). No betaling should be generated
        - Single person, multiple teams (youth teams). Betaling should contain the highest of the 2 amounts.
        - Single person, multiple teams (senior + youth). Betaling should contain amount of youth.
    """

    def test_generate_no_team(self):
        """
        Test that no betalingen are generated when a person is not in a team.
        """
        logger.info(
            "Running test to check that no betalingen are generated when a person is not in a team"
        )
        seizoen = Seizoen.objects.get(pk=1)
        lid = Lid.objects.get(pk=1)

        # Genereer betaling
        genereer_betaling(lid=lid, seizoen=seizoen)

        # Check that there is no betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 0)

    def test_generate_single_team_1(self):
        """
        Test the successful generation of Betaling for a single person in a single team.
        """
        logger.info(
            "Running test to check that a betaling is generated successfully when a person is in 1 team"
        )
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
        logger.info("There should be only 1 betaling")
        # Check that there is only 1 betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 1)

        logger.info(
            "Betaling should have the correct member, amount, seizoen, and should have 0 pay. Next to this, the mededeling should not be empty"
        )
        res_betaling = betalingen[0]
        self.assertEqual(res_betaling.lid, lid)
        self.assertEqual(res_betaling.origineel_bedrag, TEST_LIDGELD_3MAAL)
        self.assertEqual(res_betaling.afgelost_bedrag, 0)
        self.assertEqual(res_betaling.seizoen, seizoen)
        self.assertNotEqual(res_betaling.mededeling, "")

    def test_generate_single_team_2(self):
        """
        Test that no betaling is generated when the member is only in a seniors team.
        """
        logger.info(
            "Running test to check that no betaling is generated when the member is exclusively in a seniors team"
        )
        # Add ploeglid to ploeg with specific lidgeldklasse
        klasse = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_SENIOREN)
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
        self.assertEqual(len(betalingen), 0)

    def test_generate_multiple_teams_1(self):
        """
        Test the succesful generation of Betaling for a single person who is in multiple teams.
        """
        logger.info(
            "Running test to check that when a member is in multiple teams, the correct amount is generated"
        )
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

        logger.info("Check to see that there is only a single betaling")
        # Check that there is only 1 betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 1)

        logger.info(
            "Check to see that the betaling has the highest of the 2 bedragen listed."
        )
        # Betaling should be for the highest of the 2 bedragen
        res_betaling = betalingen[0]
        self.assertEqual(res_betaling.lid, lid)
        self.assertEqual(
            res_betaling.origineel_bedrag,
            max(TEST_LIDGELD_3MAAL, TEST_LIDGELD_2MAAL),
        )
        self.assertEqual(res_betaling.afgelost_bedrag, 0)
        self.assertEqual(res_betaling.seizoen, seizoen)
        self.assertNotEqual(res_betaling.mededeling, "")

    def test_generate_multiple_teams_2(self):
        """
        Test the succesful generation of Betaling for a single person in multiple teams.
        In this case, the person is in a) a youth team, and b) a senior team.
        """
        logger.info(
            "Running a test to check that when a person is in a youth team and a senior team, the correct amount is generated"
        )
        # Add the member to the 2 different teams
        klasse_1 = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_3MAAL)
        klasse_2 = LidgeldKlasse.objects.get(lidgeld=TEST_LIDGELD_SENIOREN)
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
