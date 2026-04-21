# aplicacoes/cadastros/cadastro_veiculo_apreendido/models.py
from django.db import models
from django.contrib.auth.models import User

class VeiculoApreendido(models.Model):
    # Campos básicos
    placa = models.CharField(max_length=20)
    chassi = models.CharField('Chassi', max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50)
    cor = models.CharField(max_length=30)
    ano = models.IntegerField()
    data_apreensao = models.DateField()
    local_apreensao = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)
    
    # NOVOS CAMPOS DE VISTORIA NA APREENSÃO
    CONDICAO_CHOICES = [
        ('OTIMO', 'Ótimo'),
        ('BOM', 'Bom'),
        ('REGULAR', 'Regular'),
        ('RUIM', 'Ruim'),
        ('PESSIMO', 'Péssimo'),
    ]
    
    NIVEL_COMBUSTIVEL = [
        ('1/4', '1/4'),
        ('1/2', '1/2'), 
        ('3/4', '3/4'),
        ('CHEIO', 'Cheio'),
        ('RESERVA', 'Reserva'),
    ]
    
    # Vistoria técnica
    km_atual_apreensao = models.IntegerField('Quilometragem na Apreensão', null=True, blank=True, default=0)
    nivel_combustivel = models.CharField('Nível de Combustível', max_length=20, blank=True, choices=NIVEL_COMBUSTIVEL, default='1/2')
    
    # Itens obrigatórios
    estepe_presente = models.BooleanField('Estepe presente', default=True)
    macaco_presente = models.BooleanField('Macaco presente', default=True)
    chave_roda_presente = models.BooleanField('Chave de roda presente', default=True)
    triangulo_presente = models.BooleanField('Triângulo de sinalização presente', default=True)
    cinto_seguranca_funcionando = models.BooleanField('Cintos de segurança funcionando', default=True)
    
    # Condições específicas
    condicao_pneus = models.CharField('Condição dos pneus', max_length=20, choices=CONDICAO_CHOICES, blank=True, default='BOM')
    condicao_vidros = models.CharField('Condição dos vidros', max_length=20, choices=CONDICAO_CHOICES, blank=True, default='BOM')
    condicao_lataria = models.CharField('Condição da lataria', max_length=20, choices=CONDICAO_CHOICES, blank=True, default='BOM')
    condicao_motor = models.CharField('Condição do motor', max_length=20, choices=CONDICAO_CHOICES, blank=True, default='BOM')
    condicao_interna = models.CharField('Condição interna', max_length=20, choices=CONDICAO_CHOICES, blank=True, default='BOM')
    
    # Itens internos
    radio_funcionando = models.BooleanField('Rádio funcionando', default=True)
    ar_condicionado_funcionando = models.BooleanField('Ar condicionado funcionando', default=True)
    direcao_funcionando = models.BooleanField('Direção funcionando', default=True)
    trava_eletrica_funcionando = models.BooleanField('Trava elétrica funcionando', default=True)
    vidro_eletrico_funcionando = models.BooleanField('Vidro elétrico funcionando', default=True)
    
    # Documentação
    crlv_apresentado = models.BooleanField('CRLV apresentado', default=False)
    crv_apresentado = models.BooleanField('CRV apresentado', default=False)
    cnh_condutor = models.CharField('CNH do condutor', max_length=20, blank=True)
    
    # Dados do condutor
    condutor_nome = models.CharField('Nome do condutor', max_length=200, blank=True)
    condutor_cpf = models.CharField('CPF do condutor', max_length=14, blank=True)
    condutor_rg = models.CharField('RG do condutor', max_length=20, blank=True)
    condutor_endereco = models.TextField('Endereço do condutor', blank=True)
    
    # Testemunhas
    testemunha_nome = models.CharField('Nome da testemunha', max_length=200, blank=True)
    testemunha_cpf = models.CharField('CPF da testemunha', max_length=14, blank=True)
    
    # Avarias
    avarias_descricao = models.TextField('Descrição detalhada de avarias', blank=True)
    
    # Controle
    devolvido = models.BooleanField(default=False)
    data_devolucao = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.modelo} - {self.placa}"


class DevolucaoVeiculo(models.Model):
    veiculo = models.ForeignKey(VeiculoApreendido, on_delete=models.CASCADE, related_name='devolucoes')
    
    proprietario_nome = models.CharField('Nome do Proprietário', max_length=200)
    proprietario_cpf = models.CharField('CPF', max_length=14)
    proprietario_rg = models.CharField('RG', max_length=20)
    proprietario_endereco = models.TextField('Endereço Completo')
    proprietario_telefone = models.CharField('Telefone', max_length=20)
    proprietario_email = models.EmailField('E-mail', blank=True)
    
    data_devolucao = models.DateField('Data da Devolução', auto_now_add=True)
    hora_devolucao = models.TimeField('Hora da Devolução', auto_now_add=True)
    
    ESTADO_VEICULO_CHOICES = [
        ('OTIMO', 'Ótimo'),
        ('BOM', 'Bom'),
        ('REGULAR', 'Regular'),
        ('DANIFICADO', 'Danificado'),
        ('AVARIADO', 'Avariado'),
    ]
    estado_veiculo = models.CharField('Estado do Veículo', max_length=20, choices=ESTADO_VEICULO_CHOICES)
    observacoes_veiculo = models.TextField('Observações sobre o veículo', blank=True)
    km_atual = models.IntegerField('Quilometragem Atual', null=True, blank=True)
    
    nivel_combustivel_devolucao = models.CharField('Nível de Combustível', max_length=20, blank=True)
    itens_conferidos = models.TextField('Itens conferidos na devolução', blank=True)
    avarias_novas = models.TextField('Novas avarias identificadas', blank=True)
    
    documentos_apresentados = models.TextField('Documentos Apresentados')
    
    responsavel_devolucao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='devolucoes_veiculos')
    
    assinatura_proprietario = models.BooleanField('Proprietário assinou', default=False)
    assinatura_responsavel = models.BooleanField('Responsável assinou', default=False)
    
    observacoes_gerais = models.TextField('Observações Gerais', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Devolução: {self.veiculo} - {self.data_devolucao}"
    
    class Meta:
        verbose_name = 'Devolução de Veículo'
        verbose_name_plural = 'Devoluções de Veículos'
        ordering = ['-data_devolucao']