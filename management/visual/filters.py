from django_filters import FilterSet, BooleanFilter, CharFilter, DateFromToRangeFilter
from django_filters.widgets import RangeWidget
from django.forms import TextInput, CheckboxInput
from ..models import Lid


class LidFilter(FilterSet):
    voornaam = CharFilter(
        label="Voornaam",
        field_name="voornaam",
        widget=TextInput(attrs={"class": "form-control", "placeholder": "voornaam"}),
    )

    familienaam = CharFilter(
        label="Familienaam",
        field_name="familienaam",
        widget=TextInput(attrs={"class": "form-control", "placeholder": "familienaam"}),
    )

    geboortedatum = DateFromToRangeFilter(
        field_name="geboortedatum",
        label="Geboortedatum",
        widget=RangeWidget(attrs={"type": "date", "class": "form-control"}),
    )

    actief_lid = BooleanFilter(
        label="Actief Lid",
        field_name="actief_lid",
        widget=CheckboxInput(attrs={"checked": "checked"}),
    )

    class Meta:
        model = Lid
        fields = ["voornaam", "familienaam", "geboortedatum", "actief_lid"]
