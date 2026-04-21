# aplicacoes/escala_diaria/forms.py
from django import forms
from django.utils import timezone
from aplicacoes.cadastros.cadastro_policiais.models import Policial
from aplicacoes.cadastros.cadastro_vtrs.models import Viatura
from .models import EscalaGerada

class PolicialExternoForm(forms.Form):
    """Formulário para um policial no serviço externo"""
    policial = forms.ModelChoiceField(
        queryset=Policial.objects.filter(ativo=True).order_by('patente', 'nome_guerra'),  # CORRIGIDO: 'patente' ao invés de 'graduacao'
        widget=forms.Select(attrs={'class': 'form-control policial-select'}),
        label="Policial"
    )
    viatura = forms.ModelChoiceField(
        queryset=Viatura.objects.filter(ativo=True).order_by('prefixo'),
        widget=forms.Select(attrs={'class': 'form-control viatura-select'}),
        label="Viatura"
    )
    funcao = forms.ChoiceField(
        choices=EscalaGerada.FUNCAO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control funcao-select'}),
        label="Função"
    )

class PermutaForm(forms.Form):
    """Formulário para uma permuta"""
    policial_a = forms.ModelChoiceField(
        queryset=Policial.objects.filter(ativo=True).order_by('patente', 'nome_guerra'),  # CORRIGIDO
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Policial A"
    )
    policial_b = forms.ModelChoiceField(
        queryset=Policial.objects.filter(ativo=True).order_by('patente', 'nome_guerra'),  # CORRIGIDO
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Policial B"
    )
    tipo = forms.ChoiceField(
        choices=EscalaGerada.TIPO_PERMUTA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Tipo"
    )

class DispensaForm(forms.Form):
    """Formulário para uma dispensa"""
    policial = forms.ModelChoiceField(
        queryset=Policial.objects.filter(ativo=True).order_by('patente', 'nome_guerra'),  # CORRIGIDO
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Policial"
    )
    motivo = forms.ChoiceField(
        choices=EscalaGerada.MOTIVO_DISPENSA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Motivo"
    )
    tipo = forms.ChoiceField(
        choices=EscalaGerada.TIPO_DISPENSA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Tipo"
    )

class EscalaForm(forms.Form):
    """Formulário principal da escala"""
    data_escala = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Data da Escala"
    )
    
    # Permanência
    permanencia = forms.ModelChoiceField(
        queryset=Policial.objects.filter(ativo=True).order_by('patente', 'nome_guerra'),  # CORRIGIDO
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Policial na Permanência",
        required=False
    )