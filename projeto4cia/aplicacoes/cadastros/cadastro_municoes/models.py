from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Municao(models.Model):
    calibre = models.CharField('Calibre', max_length=20)
    fabricante = models.CharField('Fabricante', max_length=100)
    modelo = models.CharField('Modelo', max_length=100)
    quantidade = models.IntegerField('Quantidade em Estoque', default=0)
    quantidade_minima = models.IntegerField('Quantidade Mínima', default=10)
    validade = models.DateField('Data de Validade')
    observacoes = models.TextField('Observações', blank=True)
    
    # Controle
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Munição'
        verbose_name_plural = 'Munições'
        ordering = ['calibre', 'fabricante', 'modelo']
        unique_together = ['calibre', 'fabricante', 'modelo', 'validade']  # Evita duplicatas

    def __str__(self):
        return f"{self.calibre} - {self.fabricante} {self.modelo}"
    
    def esta_baixo_estoque(self):
        return self.quantidade <= self.quantidade_minima
    
    def dar_baixa(self, quantidade):
        """Reduz o estoque quando a munição é cautelada"""
        if quantidade > self.quantidade:
            raise ValueError(f"Quantidade insuficiente. Disponível: {self.quantidade}")
        self.quantidade -= quantidade
        self.save()
    
    def repor_estoque(self, quantidade):
        """Aumenta o estoque quando a munição é devolvida"""
        self.quantidade += quantidade
        self.save()


class MovimentacaoMunicao(models.Model):
    """Registro de todas as movimentações de munição"""
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada (Compra/Doação)'),
        ('SAIDA_CAUTELA', 'Saída por Cautela'),
        ('DEVOLUCAO_CAUTELA', 'Devolução de Cautela'),
        ('AJUSTE', 'Ajuste de Estoque'),
    ]
    
    municao = models.ForeignKey(
        Municao,
        on_delete=models.PROTECT,
        related_name='movimentacoes'
    )
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    quantidade = models.IntegerField('Quantidade', validators=[MinValueValidator(1)])
    data_movimentacao = models.DateTimeField('Data', default=timezone.now)
    
    # Relação com cautela (se aplicável)
    cautela = models.ForeignKey(
        'cautela_armamento.Cautela',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_municao'
    )
    
    observacao = models.TextField('Observação', blank=True)
    criado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['-data_movimentacao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.municao} - {self.quantidade}"