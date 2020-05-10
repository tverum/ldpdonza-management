from django_filters import FilterSet
from .models import Lid


class LidBetalingFilter(FilterSet):
    class Meta:
        model = Lid
        fields = ['voornaam', 'familienaam', 'geboortedatum']