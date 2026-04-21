from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from aplicacoes.cadastros.cadastro_policiais.models import Policial
from aplicacoes.cadastros.cadastro_armamentos.models import Armamento
from aplicacoes.cadastros.cadastro_equipamentos.models import Equipamento
from aplicacoes.cadastros.cadastro_municoes.models import Municao  # <-- IMPORTAR

class Cautela(models.Model):
    STATUS_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('DEVOLVIDA', 'Devolvida'),
        ('PARCIAL', 'Devolução Parcial'),
        ('CANCELADA', 'Cancelada'),
    ]

    # Datas
    data_cautela = models.DateTimeField('Data da Cautela', auto_now_add=True)
    data_devolucao = models.DateTimeField('Data de Devolução', null=True, blank=True)
    data_prevista_devolucao = models.DateTimeField('Previsão de Devolução')
    
    # Policial
    policial = models.ForeignKey(
        Policial,
        on_delete=models.PROTECT,
        verbose_name='Policial',
        related_name='cautelas'
    )
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ATIVA')
    
    # Observações
    observacoes = models.TextField('Observações', blank=True)
    
    # Controle
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    criado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cautelas_criadas'
    )
    devolvido_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devolucoes_realizadas',
        verbose_name='Devolvido por'
    )
    
    class Meta:
        verbose_name = 'Cautela'
        verbose_name_plural = 'Cautelas'
        ordering = ['-data_cautela']

    def __str__(self):
        return f'Cautela #{self.id} - {self.policial.nome_guerra} - {self.data_cautela.strftime("%d/%m/%Y")}'

class ItemCautela(models.Model):
    TIPO_ITEM_CHOICES = [
        ('ARMAMENTO_PRINCIPAL', 'Armamento Principal'),
        ('ARMAMENTO_SECUNDARIO', 'Armamento Secundário'),
        ('EQUIPAMENTO', 'Equipamento'),
        ('MUNICAO', 'Munição'),
    ]

    cautela = models.ForeignKey(
        Cautela,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    
    tipo_item = models.CharField('Tipo de Item', max_length=20, choices=TIPO_ITEM_CHOICES)
    
    # Para armamentos
    armamento = models.ForeignKey(
        Armamento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Armamento'
    )
    
    # Para equipamentos
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Equipamento'
    )
    
    # Para munição - AGORA CONECTADO COM O MODELO MUNICAO
    municao = models.ForeignKey(
        Municao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Munição',
        related_name='itens_cautela'
    )
    quantidade_municao = models.IntegerField(
        'Quantidade', 
        validators=[MinValueValidator(1)], 
        null=True, 
        blank=True
    )
    
    # Para controle de lote específico (opcional)
    # lote_municao = models.ForeignKey(  # <-- CAMPO OPCIONAL PARA LOTES
    #     LoteMunicao,
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     verbose_name='Lote',
    #     related_name='itens_cautela'
    # )
    
    # Controle de devolução
    devolvido = models.BooleanField('Devolvido?', default=False)
    data_devolucao_item = models.DateTimeField('Data Devolução', null=True, blank=True)
    observacao_item = models.TextField('Observação do Item', blank=True)

    class Meta:
        verbose_name = 'Item da Cautela'
        verbose_name_plural = 'Itens da Cautela'

    def __str__(self):
        if self.armamento:
            return f'{self.get_tipo_item_display()}: {self.armamento}'
        elif self.equipamento:
            return f'{self.get_tipo_item_display()}: {self.equipamento}'
        elif self.municao:
            return f'Munição: {self.municao} - {self.quantidade_municao}'
        return f'Item #{self.id}'