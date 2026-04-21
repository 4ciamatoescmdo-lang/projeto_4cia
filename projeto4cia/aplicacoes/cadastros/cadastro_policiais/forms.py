from django import forms
from .models import Policial

class PolicialForm(forms.ModelForm):
    class Meta:
        model = Policial
        fields = [
            'nome_completo', 'nome_guerra', 'patente', 
            'matricula', 'cpf', 'telefone', 'ativo', 'observacoes'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
        }