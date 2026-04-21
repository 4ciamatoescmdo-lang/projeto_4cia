from django import forms
from .models import Eletronico

class EletronicoForm(forms.ModelForm):
    class Meta:
        model = Eletronico
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)