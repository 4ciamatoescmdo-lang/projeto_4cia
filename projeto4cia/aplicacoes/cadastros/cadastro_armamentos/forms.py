from django import forms
from .models import Armamento

class ArmamentoForm(forms.ModelForm):
    class Meta:
        model = Armamento
        fields = '__all__'
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'numero_serie': forms.TextInput(attrs={'placeholder': 'Ex: ABC12345'}),
        }