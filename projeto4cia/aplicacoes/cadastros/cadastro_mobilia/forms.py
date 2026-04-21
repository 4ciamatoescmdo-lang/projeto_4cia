from django import forms
from .models import Mobilia

class MobiliaForm(forms.ModelForm):
    class Meta:
        model = Mobilia
        fields = '__all__'