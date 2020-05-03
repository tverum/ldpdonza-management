from django import forms

from .models import Lid, Ouder, Ploeg

class LidForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LidForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            lid = kwargs['instance']
            self.fields['familieleden'].queryset = Lid.objects.exclude(club_id=lid.club_id)

    class Meta:
        model = Lid
        exclude = ["updated_at", "created_at"]
        help_texts = {
            'geboortedatum': 'Formaat: YYYY-MM-DD',
            'functies': 'Houd de SHIFT-toets ingedrukt om meerdere functies te selecteren',
            'familieleden': 'Houd de SHIFT-toets ingedrukt om meerdere functies te selecteren',
        }

class OuderForm(forms.ModelForm):
    class Meta:
        model = Ouder
        exclude = ["ouder_id"]

class PloegForm(forms.ModelForm):
    class Meta:
        model = Ploeg
        exclude = ["ploeg_id"]