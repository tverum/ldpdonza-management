import logging

from django.test import tag

from management.main.betalingen import genereer_betaling, get_discount
from management.models import (
    Betaling,
    Functie,
    Lid,
    Ploeg,
    PloegLid,
    Seizoen,
)
from management.tests.generic_test_case import GenericBetalingTestCase
from management.tests.util import (
    TEST_LIDGELD_2MAAL,
    create_basic_teams,
    create_lid_personas,
    TEST_LIDGELD_3MAAL,
)

logger = logging.getLogger(__name__)


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

    def setUp(self) -> None:
        """
        Setup function.
        Create the scaffolding to run the test.
        """
        create_basic_teams()
        create_lid_personas()
        return super().setUp()

    @tag("betaling")
    def test_generate_no_team(self):
        """
        Test that no betalingen are generated when a person is not in a team.
        """
        logger.info(
            "Running test to check that no betalingen are generated when a person is not in a team"
        )
        seizoen = Seizoen.objects.get(pk=1)
        lid = Lid.objects.get(voornaam="John", familienaam="Doe")

        # Genereer betaling
        genereer_betaling(lid=lid, seizoen=seizoen)

        # Check that there is no betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 0)

    @tag("betaling")
    def test_generate_single_team_1(self):
        """
        Test the successful generation of Betaling for a single person in a single team.
        In this case the team should be a paying team. So not MS or VS
        """
        logger.info(
            "Running test to check that a betaling is generated successfully when a person is in 1 team"
        )
        seizoen = Seizoen.objects.get(pk=1)
        mannen_jeugd_3 = Ploeg.objects.get(korte_naam="MJ3")
        john = Lid.objects.get(voornaam="John", familienaam="Doe")

        PloegLid.objects.create(
            ploeg=mannen_jeugd_3,
            lid=john,
            functie=Functie.objects.get(functie="Speler"),
        )

        # Genereer betaling
        genereer_betaling(lid=john, seizoen=seizoen)
        # Check that there is only 1 betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 1)

        res_betaling = betalingen[0]
        self.assertEqual(res_betaling.lid, john)
        self.assertEqual(res_betaling.origineel_bedrag, TEST_LIDGELD_3MAAL)
        self.assertEqual(res_betaling.afgelost_bedrag, 0)
        self.assertEqual(res_betaling.seizoen, seizoen)
        self.assertNotEqual(res_betaling.mededeling, "")

    @tag("betaling")
    def test_generate_single_team_2(self):
        """
        Test that no betaling is generated when the member is only in a seniors team.
        """
        logger.info(
            "Running test to check that no betaling is generated when the member is exclusively in a seniors team"
        )
        # Add ploeglid to ploeg with specific lidgeldklasse
        seizoen = Seizoen.objects.get(pk=1)
        mannen_senioren = Ploeg.objects.get(korte_naam="MS")
        john = Lid.objects.get(pk=1)

        PloegLid.objects.create(
            ploeg=mannen_senioren,
            lid=john,
            functie=Functie.objects.get(functie="Speler"),
        )

        # Genereer betaling
        genereer_betaling(lid=john, seizoen=seizoen)

        # Check that there is only 1 betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 0)

    @tag("betaling")
    def test_generate_multiple_teams_1(self):
        """
        Test the succesful generation of Betaling for a single person who is in multiple teams.
        """
        logger.info(
            "Running test to check that when a member is in multiple teams, the correct amount is generated"
        )
        # Add the member to the 2 different teams
        huidig_seizoen = Seizoen.objects.get(pk=1)
        mannen_jeugd_3 = Ploeg.objects.get(korte_naam="MJ3")
        mannen_jeugd_2 = Ploeg.objects.get(korte_naam="MJ2")
        john = Lid.objects.get(voornaam="John", familienaam="Doe")

        PloegLid.objects.create(
            ploeg=mannen_jeugd_3,
            lid=john,
            functie=Functie.objects.get(functie="Speler"),
        )
        PloegLid.objects.create(
            ploeg=mannen_jeugd_2,
            lid=john,
            functie=Functie.objects.get(functie="Speler"),
        )

        # Genereer betaling
        genereer_betaling(lid=john, seizoen=huidig_seizoen)

        # Check that there is only 1 betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 1)
        # Betaling should be for the highest of the 2 bedragen
        res_betaling = betalingen[0]
        self.assertEqual(res_betaling.lid, john)
        self.assertEqual(
            res_betaling.origineel_bedrag,
            max(TEST_LIDGELD_3MAAL, TEST_LIDGELD_2MAAL),
        )
        self.assertEqual(res_betaling.afgelost_bedrag, 0)
        self.assertEqual(res_betaling.seizoen, huidig_seizoen)
        self.assertNotEqual(res_betaling.mededeling, "")

    @tag("betaling")
    def test_generate_multiple_teams_2(self):
        """
        Test the succesful generation of Betaling for a single person in multiple teams.
        In this case, the person is in a) a youth team, and b) a senior team.
        """
        logger.info(
            "Running a test to check that when a person is in a youth team and a senior team, the correct amount is generated."
        )
        seizoen = Seizoen.objects.get(pk=1)
        mannen_jeugd_3 = Ploeg.objects.get(korte_naam="MJ3")
        mannen_senioren = Ploeg.objects.get(korte_naam="MS")
        john = Lid.objects.get(voornaam="John", familienaam="Doe")

        PloegLid.objects.create(
            ploeg=mannen_jeugd_3,
            lid=john,
            functie=Functie.objects.get(functie="Speler"),
        )
        PloegLid.objects.create(
            ploeg=mannen_senioren,
            lid=john,
            functie=Functie.objects.get(functie="Speler"),
        )

        # Genereer betaling
        genereer_betaling(lid=john, seizoen=seizoen)

        # Check that there is only 1 betaling generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 1)

        res_betaling = betalingen[0]
        self.assertEqual(res_betaling.lid, john)
        self.assertEqual(res_betaling.origineel_bedrag, TEST_LIDGELD_3MAAL)
        self.assertEqual(res_betaling.afgelost_bedrag, 0)
        self.assertEqual(res_betaling.seizoen, seizoen)
        self.assertNotEqual(res_betaling.mededeling, "")

    @tag("betaling")
    def test_generate_with_family_member(self):
        """
        Test the successful generation of Betaling for a person that has an older sibling at the club.
        In this case, their should be a €50 discount.
        """
        logger.info(
            "Running a test to check that when a person has (an) older sibling(s), they get a 50 euro discount."
        )

        seizoen = Seizoen.objects.get(pk=1)
        mannen_jeugd_3 = Ploeg.objects.get(korte_naam="MJ3")
        vrouwen_jeugd_3 = Ploeg.objects.get(korte_naam="VJ3")
        john = Lid.objects.get(voornaam="John", familienaam="Doe")
        jane = Lid.objects.get(voornaam="Jane", familienaam="Doe")

        PloegLid.objects.create(
            ploeg=mannen_jeugd_3,
            lid=john,
            functie=Functie.objects.get(functie="Speler"),
        )
        PloegLid.objects.create(
            ploeg=vrouwen_jeugd_3,
            lid=jane,
            functie=Functie.objects.get(functie="Speler"),
        )

        discount_oudste = get_discount(john, seizoen)
        discount_jongste = get_discount(jane, seizoen)
        genereer_betaling(lid=john, seizoen=seizoen)
        genereer_betaling(lid=jane, seizoen=seizoen)

        # Two betalingen should be generated
        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 2)

        # Check betaling voor oudste lid
        oud_betaling = betalingen.get(lid=john)
        jong_betaling = betalingen.get(lid=jane)
        self.assertEqual(discount_oudste, 0)
        self.assertEqual(discount_jongste, 50)
        self.assertEqual(oud_betaling.origineel_bedrag, TEST_LIDGELD_3MAAL)
        self.assertEqual(
            jong_betaling.origineel_bedrag, TEST_LIDGELD_3MAAL - 50
        )

    @tag("betaling")
    def test_generate_with_family_member_2(self):
        """
        Test that when both siblings play for senior teams, ther is no betaling generated.
        """
        logger.info(
            "Running a test case to chack that when 2 siblings play in senior teams, still no betaling is generated."
        )
        seizoen = Seizoen.objects.get(pk=1)
        mannen_senioren = Ploeg.objects.get(korte_naam="MS")
        vrouwen_senioren = Ploeg.objects.get(korte_naam="VS")
        john = Lid.objects.get(voornaam="John", familienaam="Doe")
        jane = Lid.objects.get(voornaam="Jane", familienaam="Doe")

        PloegLid.objects.create(
            ploeg=mannen_senioren,
            lid=john,
            functie=Functie.objects.get(functie="Speler"),
        )
        PloegLid.objects.create(
            ploeg=vrouwen_senioren,
            lid=jane,
            functie=Functie.objects.get(functie="Speler"),
        )

        genereer_betaling(lid=john, seizoen=seizoen)
        genereer_betaling(lid=jane, seizoen=seizoen)

        betalingen = Betaling.objects.all()
        self.assertEqual(len(betalingen), 0)
