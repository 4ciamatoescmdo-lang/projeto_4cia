from django import forms
from .models import Viatura

class ViaturaForm(forms.ModelForm):
    class Meta:
        model = Viatura
        fields = [
            'prefixo', 'placa', 'tipo', 'marca', 'modelo', 
            'ano', 'cor', 'renavam', 'chassi', 'km_atual',
            'status', 'observacoes', 'ativo'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'placa': forms.TextInput(attrs={'placeholder': 'ABC-1234'}),
            'km_atual': forms.NumberInput(attrs={'min': 0}),
            'ano': forms.NumberInput(attrs={'min': 1990, 'max': 2026}),
        }