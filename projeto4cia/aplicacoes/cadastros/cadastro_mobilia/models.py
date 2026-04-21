from django.db import models

class Mobilia(models.Model):
    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('EM_USO', 'Em Uso'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('BAIXADO', 'Baixado'),
    ]
    
    TIPO_CHOICES = [
        ('MESA', 'Mesa'),
        ('CADEIRA', 'Cadeira'),
        ('ARMARIO', 'Armário'),
        ('ESTANTE', 'Estante'),
        ('SOFA', 'Sofá'),
        ('BELICHE', 'Beliche'),
        ('GUARDA', 'Guarda-volumes'),
        ('BANQUETA', 'Banqueta'),
        ('BALCAO', 'Balcão'),
        ('OUTROS', 'Outros'),
    ]

    MATERIAL_CHOICES = [
        ('MADEIRA', 'Madeira'),
        ('METAL', 'Metal'),
        ('PLASTICO', 'Plástico'),
        ('VIDRO', 'Vidro'),
        ('MISTO', 'Misto'),
    ]

    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    descricao = models.CharField('Descrição', max_length=200)
    material = models.CharField('Material', max_length=20, choices=MATERIAL_CHOICES)
    
    # Identificação
    patrimonio = models.CharField('Nº Patrimônio', max_length=30, unique=True, blank=True, null=True)
    
    # Características
    dimensoes = models.CharField('Dimensões (LxPxA)', max_length=50, blank=True, 
                                 help_text='Ex: 1.50x0.80x0.75')
    cor = models.CharField('Cor', max_length=50, blank=True)
    
    # Localização
    localizacao = models.CharField('Localização (Sala/Setor)', max_length=100)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')
    estado_conservacao = models.TextField('Estado de Conservação', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    
    # Controle
    ativo = models.BooleanField('Ativo?', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Mobília'
        verbose_name_plural = 'Mobílias'
        ordering = ['tipo', 'descricao']

    def __str__(self):
        return f'{self.get_tipo_display()} {self.descricao} - {self.localizacao}'