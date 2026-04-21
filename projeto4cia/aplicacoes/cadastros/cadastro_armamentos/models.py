from django.db import models

class Armamento(models.Model):
    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('EM_USO', 'Em Uso'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('BAIXADO', 'Baixado'),
    ]
    
    CALIBRE_CHOICES = [
        ('.22', '.22'),
        ('.32', '.32'),
        ('.38', '.38'),
        ('9mm', '9mm'),
        ('.40', '.40'),
        ('.45', '.45'),
        ('12', 'Calibre 12'),
        ('5.56', '5.56mm'),
        ('7.62', '7.62mm'),
    ]

    TIPO_CHOICES = [
        ('PISTOLA', 'Pistola'),
        ('REVOLVER', 'Revólver'),
        ('FUZIL', 'Fuzil'),
        ('CARABINA', 'Carabina'),
        ('ESPINGARDA', 'Espingarda'),
        ('SUBMETRALHADORA', 'Submetralhadora'),
        ('METRALHADORA', 'Metralhadora'),
    ]

    numero_serie = models.CharField('Nº de Série', max_length=50, unique=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    marca = models.CharField('Marca', max_length=50)
    modelo = models.CharField('Modelo', max_length=50)
    calibre = models.CharField('Calibre', max_length=10, choices=CALIBRE_CHOICES)
    
    # Identificação
    patrimonio = models.CharField('Nº Patrimônio', max_length=30, blank=True, null=True)
    registro = models.CharField('Nº Registro', max_length=30, blank=True)
    
    # Características
    capacidade = models.IntegerField('Capacidade (tiros)', default=0)
    comprimento_cano = models.DecimalField('Comprimento do Cano (cm)', max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')
    observacoes = models.TextField('Observações', blank=True)
    
    # Controle
    ativo = models.BooleanField('Ativo?', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Armamento'
        verbose_name_plural = 'Armamentos'
        ordering = ['tipo', 'marca', 'modelo']

    def __str__(self):
        return f'{self.get_tipo_display()} {self.marca} {self.modelo} - {self.numero_serie}'