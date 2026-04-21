from django.db import models

class Equipamento(models.Model):
    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('EM_USO', 'Em Uso'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('BAIXADO', 'Baixado'),
    ]
    
    CATEGORIA_CHOICES = [
        ('PROTECAO', 'Proteção Individual'),
        ('COMUNICACAO', 'Comunicação'),
        ('ILUMINACAO', 'Iluminação'),
        ('FERRAMENTAS', 'Ferramentas'),
        ('PRISAO', 'Material de Prisão'),
        ('OUTROS', 'Outros'),
    ]

    UNIDADE_CHOICES = [
        ('UN', 'Unidade'),
        ('PAR', 'Par'),
        ('CONJ', 'Conjunto'),
        ('KIT', 'Kit'),
    ]

    nome = models.CharField('Nome do Equipamento', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES)
    marca = models.CharField('Marca', max_length=50, blank=True)
    modelo = models.CharField('Modelo', max_length=50, blank=True)
    
    # Identificação
    patrimonio = models.CharField('Nº Patrimônio', max_length=30, unique=True, blank=True, null=True)
    numero_serie = models.CharField('Nº de Série', max_length=50, blank=True)
    
    # Datas
    data_fabricacao = models.DateField('Data de Fabricação', blank=True, null=True)
    data_vencimento = models.DateField('Data de Vencimento', blank=True, null=True)
    
    # Controle
    quantidade = models.IntegerField('Quantidade', default=1)
    unidade = models.CharField('Unidade', max_length=10, choices=UNIDADE_CHOICES, default='UN')
    quantidade_minima = models.IntegerField('Quantidade Mínima', default=1)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')
    localizacao = models.CharField('Localização', max_length=100, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    
    # Controle
    ativo = models.BooleanField('Ativo?', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
        ordering = ['categoria', 'nome']

    def __str__(self):
        return f'{self.nome} - {self.marca} {self.modelo}/{self.numero_serie}'
    
    def precisa_repor(self):
        return self.quantidade <= self.quantidade_minima