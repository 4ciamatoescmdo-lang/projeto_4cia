# aplicacoes/cadastros/cadastro_veiculo_apreendido/forms.py
from django import forms
from .models import VeiculoApreendido, DevolucaoVeiculo

class VeiculoApreendidoForm(forms.ModelForm):
    class Meta:
        model = VeiculoApreendido
        fields = '__all__'
        exclude = ['devolvido', 'data_devolucao']
        
        widgets = {
            'data_apreensao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ABC-1234'}),
            'chassi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do Chassi'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'local_apreensao': forms.TextInput(attrs={'class': 'form-control'}),
            'km_atual_apreensao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'KM atual'}),
            'nivel_combustivel': forms.Select(attrs={'class': 'form-control'}),
            'condicao_pneus': forms.Select(attrs={'class': 'form-control'}),
            'condicao_vidros': forms.Select(attrs={'class': 'form-control'}),
            'condicao_lataria': forms.Select(attrs={'class': 'form-control'}),
            'condicao_motor': forms.Select(attrs={'class': 'form-control'}),
            'condicao_interna': forms.Select(attrs={'class': 'form-control'}),
            'avarias_descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva detalhadamente avarias...'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cnh_condutor': forms.TextInput(attrs={'class': 'form-control'}),
            'condutor_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'condutor_cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'condutor_rg': forms.TextInput(attrs={'class': 'form-control'}),
            'condutor_endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'testemunha_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'testemunha_cpf': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'placa': 'Placa *',
            'modelo': 'Modelo *',
            'cor': 'Cor *',
            'ano': 'Ano *',
            'data_apreensao': 'Data da Apreensão *',
            'local_apreensao': 'Local da Apreensão *',
            'km_atual_apreensao': 'Quilometragem na Apreensão',
            'nivel_combustivel': 'Nível de Combustível',
            'estepe_presente': '✓ Estepe presente',
            'macaco_presente': '✓ Macaco presente',
            'chave_roda_presente': '✓ Chave de roda presente',
            'triangulo_presente': '✓ Triângulo presente',
            'cinto_seguranca_funcionando': '✓ Cintos funcionando',
            'radio_funcionando': '✓ Rádio funcionando',
            'ar_condicionado_funcionando': '✓ Ar condicionado funcionando',
            'direcao_funcionando': '✓ Direção funcionando',
            'trava_eletrica_funcionando': '✓ Trava elétrica funcionando',
            'vidro_eletrico_funcionando': '✓ Vidro elétrico funcionando',
            'crlv_apresentado': '✓ CRLV apresentado',
            'crv_apresentado': '✓ CRV apresentado',
        }


class DevolucaoVeiculoForm(forms.ModelForm):
    class Meta:
        model = DevolucaoVeiculo
        exclude = ['veiculo', 'responsavel_devolucao', 'data_devolucao', 'hora_devolucao', 'created_at']
        widgets = {
            'proprietario_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'proprietario_cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'proprietario_rg': forms.TextInput(attrs={'class': 'form-control'}),
            'proprietario_endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proprietario_telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'proprietario_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'estado_veiculo': forms.Select(attrs={'class': 'form-control'}),
            'observacoes_veiculo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'km_atual': forms.NumberInput(attrs={'class': 'form-control'}),
            'nivel_combustivel_devolucao': forms.Select(attrs={'class': 'form-control'}),
            'itens_conferidos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avarias_novas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documentos_apresentados': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assinatura_proprietario': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'assinatura_responsavel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes_gerais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }