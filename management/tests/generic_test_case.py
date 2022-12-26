"""
This file contains generic test cases to be reused.
These contain some abstract, generic functionality to be reused by implementing classes.
Examples are:
1. Each testcase should most likely have some data available:
    - A season to work in
    - The following functions available: Speler, Coach
2. For betalings-testcases, there should be
    - Some ploegen
    - Some lidgeldklasses
    - Some leden
"""

from django.test import TestCase


class GenericTestCase(TestCase):
    """
    This is a generic test case that contains logic for all test cases to reuse.
    It loads the functies, lidgeldklasses & seizoenen

    Inherits from django.test.TestCase
    """

    fixtures = [
        "fixtures/fixture_functie_lgklasse.json",  # Load in functies & lidgeldklasses
        "fixtures/fixture_seizoen.json",  # Load in 2 seizoenen
    ]


class GenericBetalingTestCase(GenericTestCase):
    """
    This is a generic test case for betalingen.
    It loads functies, lidgeldklasses & 2 seizoenen.
    It creates 5 teams (1 for each lidgeldklasse) and creates 3 leden.

    It inherits from the GenericTestCase
    """

    fixtures = [
        "fixture_functie_lgklasse.json",
        "fixture_seizoen.json",
        "fixture_ploeg.json",
        "fixture_lid.json",
    ]
