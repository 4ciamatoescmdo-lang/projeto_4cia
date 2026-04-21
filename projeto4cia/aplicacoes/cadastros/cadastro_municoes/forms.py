from django import forms
from .models import Municao

class MunicaoForm(forms.ModelForm):
    class Meta:
        model = Municao
        fields = ['calibre', 'fabricante', 'modelo', 'quantidade', 'validade', 'observacoes']
        widgets = {
            'validade': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'validade': 'Data de Validade *',
        }