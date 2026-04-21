from django.db import models

class Viatura(models.Model):
    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('EM_USO', 'Em Uso'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('BAIXADA', 'Baixada'),
    ]
    
    TIPO_CHOICES = [
        ('PICKUP', 'Pickup'),
        ('SUV', 'SUV'),
        ('SEDAN', 'Sedan'),
        ('MOTO', 'Motocicleta'),
        ('CAMINHAO', 'Caminhão'),
        ('ONIBUS', 'Ônibus'),
    ]

    prefixo = models.CharField('Prefixo', max_length=20, unique=True)
    placa = models.CharField('Placa', max_length=8, unique=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    marca = models.CharField('Marca', max_length=50)
    modelo = models.CharField('Modelo', max_length=50)
    ano = models.IntegerField('Ano')
    cor = models.CharField('Cor', max_length=30)
    
    # Características
    renavam = models.CharField('Renavam', max_length=20, blank=True)
    chassi = models.CharField('Chassi', max_length=30, blank=True)
    km_atual = models.IntegerField('Quilometragem Atual', default=0)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')
    observacoes = models.TextField('Observações', blank=True)
    
    # Controle
    ativo = models.BooleanField('Ativo?', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Viatura'
        verbose_name_plural = 'Viaturas'
        ordering = ['prefixo']

    def __str__(self):
        return f'{self.prefixo} - {self.marca} {self.modelo} ({self.placa})'