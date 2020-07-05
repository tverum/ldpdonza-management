import random

from ..models import Lid


def generate_uid():
    """
    Generate a random 10-digit UID
    :return: a random integer consisting of 10-digits
    """
    result = random.randint(1000000000, 9999999999)
    while uid_is_used(result):
        result = random.randint(1000000000, 9999999999)
    return result


def uid_is_used(uid):
    """
    Check if a uid has already been used
    :param uid: the uid to check
    :return: boolean that indicates if the uid is already used
    """
    return uid in [lid.uid for lid in Lid.objects.all()]
