from django.db import models

class Eletronico(models.Model):
    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('EM_USO', 'Em Uso'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('BAIXADO', 'Baixado'),
    ]
    
    TIPO_CHOICES = [
        ('COMPUTADOR', 'Computador'),
        ('NOTEBOOK', 'Notebook'),
        ('TABLET', 'Tablet'),
        ('CELULAR', 'Celular'),
        ('RADIO', 'Rádio Comunicador'),
        ('IMPRESSORA', 'Impressora'),
        ('SCANNER', 'Scanner'),
        ('CAMERA', 'Câmera'),
        ('GPS', 'GPS'),
        ('SERVIDOR', 'Servidor'),
        ('SWITCH', 'Switch de Rede'),
        ('ROTEADOR', 'Roteador'),
        ('MODEM', 'Modem'),
        ('ACCESS_POINT', 'Access Point'),
        ('HD_EXTERNO', 'HD Externo'),
        ('SSD', 'SSD'),
        ('PENDRIVE', 'Pendrive'),
        ('MONITOR', 'Monitor'),
        ('TECLADO', 'Teclado'),
        ('MOUSE', 'Mouse'),
        ('WEBCAM', 'Webcam'),
        ('MICROFONE', 'Microfone'),
        ('HEADSET', 'Headset'),
        ('CAIXA_SOM', 'Caixa de Som'),
        ('PROJETOR', 'Projetor'),
        ('NOBREAK', 'Nobreak'),
        ('ESTABILIZADOR', 'Estabilizador'),
        ('SMART_TV', 'Smart TV'),
        ('DRONE', 'Drone'),
        ('VIDEO_GAME', 'Videogame'),
        ('LEITOR_BIOMETRICO', 'Leitor Biométrico'),
        ('LEITOR_CODIGO_BARRAS', 'Leitor de Código de Barras'),
        ('IMPRESSORA_TERMICA', 'Impressora Térmica'),
        ('PLOTTER', 'Plotter'),
        ('OUTROS', 'Outros'),
    ]

    SISTEMA_CHOICES = [
        ('WINDOWS', 'Windows'),
        ('LINUX', 'Linux'),
        ('MACOS', 'MacOS'),
        ('ANDROID', 'Android'),
        ('IOS', 'iOS'),
        ('OUTRO', 'Outro'),
    ]

    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    marca = models.CharField('Marca', max_length=50)
    modelo = models.CharField('Modelo', max_length=50)
    
    # Identificação
    patrimonio = models.CharField('Nº Patrimônio', max_length=30, unique=True, blank=True, null=True)
    numero_serie = models.CharField('Nº de Série', max_length=50, unique=True)
    
    # Especificações
    processador = models.CharField('Processador', max_length=100, blank=True)
    memoria_ram = models.CharField('Memória RAM', max_length=20, blank=True)
    armazenamento = models.CharField('Armazenamento', max_length=20, blank=True)
    sistema_operacional = models.CharField('Sistema Operacional', max_length=20, choices=SISTEMA_CHOICES, blank=True)
    
    # Acessórios
    possui_carregador = models.BooleanField('Possui Carregador?', default=True)
    possui_bateria = models.BooleanField('Possui Bateria?', default=True)
    observacoes_acessorios = models.TextField('Observações sobre acessórios', blank=True)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')
    localizacao = models.CharField('Localização', max_length=100, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    
    # Controle
    ativo = models.BooleanField('Ativo?', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Eletrônico'
        verbose_name_plural = 'Eletrônicos'
        ordering = ['tipo', 'marca', 'modelo']

    def __str__(self):
        return f'{self.get_tipo_display()} {self.marca} {self.modelo} - {self.numero_serie}'