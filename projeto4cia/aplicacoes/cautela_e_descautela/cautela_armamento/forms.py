from django import forms
from django.utils import timezone
from .models import Cautela
from aplicacoes.cadastros.cadastro_policiais.models import Policial
from aplicacoes.cadastros.cadastro_armamentos.models import Armamento
from aplicacoes.cadastros.cadastro_equipamentos.models import Equipamento
from aplicacoes.cadastros.cadastro_municoes.models import Municao

class CautelaForm(forms.ModelForm):
    # Campos para os itens
    armamento_principal = forms.ModelChoiceField(
        queryset=Armamento.objects.filter(status='DISPONIVEL', ativo=True),
        required=False,
        label='Armamento Principal',
        empty_label="---------"
    )
    
    armamento_secundario = forms.ModelChoiceField(
        queryset=Armamento.objects.filter(status='DISPONIVEL', ativo=True),
        required=False,
        label='Armamento Secundário',
        empty_label="---------"
    )
    
    equipamento_01 = forms.ModelChoiceField(
        queryset=Equipamento.objects.filter(status='DISPONIVEL', ativo=True),
        required=False,
        label='Equipamento 01',
        empty_label="---------"
    )
    
    equipamento_02 = forms.ModelChoiceField(
        queryset=Equipamento.objects.filter(status='DISPONIVEL', ativo=True),
        required=False,
        label='Equipamento 02',
        empty_label="---------"
    )
    
    equipamento_03 = forms.ModelChoiceField(
        queryset=Equipamento.objects.filter(status='DISPONIVEL', ativo=True),
        required=False,
        label='Equipamento 03',
        empty_label="---------"
    )
    
    equipamento_04 = forms.ModelChoiceField(
        queryset=Equipamento.objects.filter(status='DISPONIVEL', ativo=True),
        required=False,
        label='Equipamento 04',
        empty_label="---------"
    )
    
    # Munição 01 - FILTRADA POR ESTOQUE > 0
    tipo_municao_01 = forms.ModelChoiceField(
        queryset=Municao.objects.filter(quantidade__gt=0),  # Só mostra com estoque
        required=False,
        label='Tipo de Munição 01',
        empty_label="---------"
    )
    quantidade_municao_01 = forms.IntegerField(
        required=False,
        label='Quantidade 01',
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )
    
    # Munição 02 - FILTRADA POR ESTOQUE > 0
    tipo_municao_02 = forms.ModelChoiceField(
        queryset=Municao.objects.filter(quantidade__gt=0),  # Só mostra com estoque
        required=False,
        label='Tipo de Munição 02',
        empty_label="---------"
    )
    quantidade_municao_02 = forms.IntegerField(
        required=False,
        label='Quantidade 02',
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    class Meta:
        model = Cautela
        fields = ['policial', 'data_prevista_devolucao', 'observacoes']
        widgets = {
            'data_prevista_devolucao': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['policial'].queryset = Policial.objects.filter(ativo=True)
        self.fields['policial'].label = 'Escolha o Policial'
        self.fields['data_prevista_devolucao'].initial = timezone.now() + timezone.timedelta(days=1)

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar se pelo menos um item foi selecionado
        tem_item = False
        
        # Verificar armamentos
        if cleaned_data.get('armamento_principal'):
            tem_item = True
        if cleaned_data.get('armamento_secundario'):
            tem_item = True
            
        # Verificar equipamentos
        for i in range(1, 5):
            if cleaned_data.get(f'equipamento_0{i}'):
                tem_item = True
                
        # Verificar munições
        if cleaned_data.get('tipo_municao_01') and cleaned_data.get('quantidade_municao_01'):
            tem_item = True
        if cleaned_data.get('tipo_municao_02') and cleaned_data.get('quantidade_municao_02'):
            tem_item = True
            
        if not tem_item:
            raise forms.ValidationError('Selecione pelo menos um item para cautelar.')
        
        # ===== VALIDAÇÃO DE ESTOQUE PARA MUNIÇÕES =====
        # Validar munição 01
        municao_01 = cleaned_data.get('tipo_municao_01')
        qtd_01 = cleaned_data.get('quantidade_municao_01')
        
        if municao_01 and qtd_01:
            if qtd_01 > municao_01.quantidade:
                raise forms.ValidationError(
                    f'Estoque insuficiente para {municao_01}. Disponível: {municao_01.quantidade}'
                )
        
        # Validar munição 02
        municao_02 = cleaned_data.get('tipo_municao_02')
        qtd_02 = cleaned_data.get('quantidade_municao_02')
        
        if municao_02 and qtd_02:
            if qtd_02 > municao_02.quantidade:
                raise forms.ValidationError(
                    f'Estoque insuficiente para {municao_02}. Disponível: {municao_02.quantidade}'
                )
        
        return cleaned_data