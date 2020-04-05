from django import forms

from .models import Lid

class LidForm(forms.ModelForm):
    
    class Meta:
        model = Lid
        exclude = ["updated_at", "created_at"]