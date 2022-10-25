from bootstrap_modal_forms.forms import BSModalForm
from django import forms

from ..models import Lid, Ouder, Ploeg


class LidForm(forms.ModelForm):

    # Define the queryset for the familieleden selector
    def __init__(self, *args, **kwargs):
        super(LidForm, self).__init__(*args, **kwargs)
        if "instance" in kwargs:
            lid = kwargs["instance"]
            queryset = (
                Lid.objects.extra(
                    select={
                        "sort": "SELECT CASE WHEN familienaam = %s THEN 0 ELSE 1 END"
                    },
                    select_params=(lid.familienaam,),
                )
                .exclude(club_id=lid.club_id)
                .order_by("sort")
            )
            self.fields["familieleden"].queryset = queryset

    class Meta:
        model = Lid
        exclude = ["updated_at", "created_at", "uid"]
        help_texts = {
            "functies": "Houd de SHIFT-toets ingedrukt om meerdere functies te selecteren",
            "familieleden": "Houd de SHIFT-toets ingedrukt om meerdere familieleden te selecteren",
        }
        widgets = {
            "voornaam": forms.TextInput(attrs={"placeholder": "Voornaam"}),
            "familienaam": forms.TextInput(
                attrs={"placeholder": "Familienaam"}
            ),
            "geboortedatum": forms.DateInput(
                attrs={"placeholder": "YYYY-MM-DD"}
            ),
            "straatnaam_en_huisnummer": forms.TextInput(
                attrs={"placeholder": "e.g. Teststraat 123 Bus A"}
            ),
            "postcode": forms.NumberInput(attrs={"placeholder": "e.g. 9800"}),
            "gemeente": forms.TextInput(attrs={"placeholder": "e.g. Deinze"}),
            "extra_informatie": forms.Textarea(
                attrs={"placeholder": "Hier komt eventuele extra informatie"}
            ),
        }


class LidModalForm(BSModalForm):
    class Meta:
        model = Lid
        fields = [
            "voornaam",
            "familienaam",
            "straatnaam_en_huisnummer",
            "postcode",
            "gemeente",
            "geboortedatum",
            "gsmnummer",
            "email",
        ]


class OuderForm(forms.ModelForm):
    class Meta:
        model = Ouder
        exclude = ["ouder_id"]


class PloegForm(forms.ModelForm):
    class Meta:
        model = Ploeg
        exclude = ["ploeg_id"]
        help_texts = {
            "min_geboortejaar": "Dit is (onder normale omstandigheden) het oudst dat een speler mag zijn voor deze leeftijdscategorie, laat leeg voor Seniorenploegen",
            "max_geboortejaar": "Dit is (onder normale omstandigheden) het jongst dat een speler mag zijn voor deze leeftijdscategorie",
            "uitzonderings_geboortejaar": 'Dit is het jongst dat een speler kan zijn, uitzonderingsgevallen waarbij een speler een jaar hoger speelt meegerekend. Als er geen uitzonderingen mogelijk zijn, vul hetzelfde in als "min jaar"',
        }
