from django import forms

from .models import Lid, Ouder, Ploeg

class LidForm(forms.ModelForm):
    class Meta:
        model = Lid
        exclude = ["updated_at", "created_at"]
        help_texts = {
            'geboortedatum': 'Formaat: YYYY/MM/DD',
        }

class OuderForm(forms.ModelForm):
    class Meta:
        model = Ouder
        exclude = ["ouder_id"]

class PloegForm(forms.ModelForm):
    class Meta:
        model = Ploeg
        exclude = ["ploeg_id"]