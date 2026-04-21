from django import forms
from .models import RelatorioAnalitico, PessoaEnvolvida

class RelatorioAnaliticoForm(forms.ModelForm):
    class Meta:
        model = RelatorioAnalitico
        fields = '__all__'
        widgets = {
            'data_ocorrencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_ocorrencia': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'relato': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
            'providencias': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_ocorrencia': forms.TextInput(attrs={'class': 'form-control'}),
            'instrumento_usado': forms.TextInput(attrs={'class': 'form-control'}),
            'materiais_apreendidos': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'viaturas_guarnicoes': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PessoaEnvolvidaForm(forms.ModelForm):
    class Meta:
        model = PessoaEnvolvida
        fields = ['tipo', 'nome', 'cpf', 'rg', 'endereco', 'nome_mae']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF'}),
            'rg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RG'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Endereço'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da mãe'}),
        }