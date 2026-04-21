from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone

class RelatorioAnalitico(models.Model):
    """
    Modelo principal para armazenar relatórios analíticos da Polícia Militar
    """
    
    # Tipos de pessoa envolvida
    TIPO_PESSOA_CHOICES = [
        ('acusado', 'Acusado'),
        ('vitima', 'Vítima'),
        ('testemunha', 'Testemunha'),
    ]
    
    # DADOS INFORMATIVOS
    numero_relatorio = models.CharField(
        max_length=50,
        verbose_name='Número do Relatório',
        help_text='Número automático do relatório (ex: 001/2024)'
    )
    
    codigo_ocorrencia = models.CharField(
        max_length=100,
        verbose_name='Código/Tipo da ocorrência',
        blank=True,
        null=True
    )
    
    local = models.TextField(
        verbose_name='Local',
        help_text='Endereço completo da ocorrência'
    )
    
    data_ocorrencia = models.DateField(
        verbose_name='Data da ocorrência',
        default=timezone.now
    )
    
    hora_ocorrencia = models.TimeField(
        verbose_name='Hora da ocorrência',
        default=timezone.now
    )
    
    instrumento_usado = models.CharField(
        max_length=200,
        verbose_name='Instrumento usado',
        blank=True,
        null=True
    )
    
    materiais_apreendidos = models.TextField(
        verbose_name='Materiais apreendidos',
        blank=True,
        null=True,
        help_text='Armas, veículos, drogas, objetos etc...'
    )
    
    # Solução da ocorrência (checkboxes)
    evadiu_se = models.BooleanField(
        default=False,
        verbose_name='Evadiu-se do local'
    )
    
    samu_acionado = models.BooleanField(
        default=False,
        verbose_name='SAMU acionado'
    )
    
    conduzido_delegacia = models.BooleanField(
        default=False,
        verbose_name='Conduzido à Delegacia'
    )
    
    viaturas_guarnicoes = models.CharField(
        max_length=500,
        verbose_name='Viaturas e guarnições envolvidas',
        blank=True,
        null=True,
        help_text='Ex: VTR 1234 - CB Silva, SD Santos'
    )
    
    # RELATO DA OCORRÊNCIA
    relato = models.TextField(
        verbose_name='Relato da ocorrência',
        help_text='Descreva detalhadamente o ocorrido'
    )
    
    # PROVIDÊNCIAS ADOTADAS
    providencias = models.TextField(
        verbose_name='Providências adotadas',
        help_text='Descreva as providências adotadas pela guarnição'
    )
    
    # METADADOS
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    criado_por = models.CharField(
        max_length=100,
        verbose_name='Criado por',
        blank=True,
        null=True,
        help_text='Nome do responsável pelo relatório'
    )
    
    # Campos de controle
    status = models.CharField(
        max_length=20,
        choices=[
            ('rascunho', 'Rascunho'),
            ('finalizado', 'Finalizado'),
            ('arquivado', 'Arquivado'),
        ],
        default='finalizado',
        verbose_name='Status'
    )
    
    class Meta:
        verbose_name = 'Relatório Analítico'
        verbose_name_plural = 'Relatórios Analíticos'
        ordering = ['-data_ocorrencia', '-criado_em']
        indexes = [
            models.Index(fields=['data_ocorrencia']),
            models.Index(fields=['numero_relatorio']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.numero_relatorio} - {self.data_ocorrencia}"
    
    def get_solucao_resumo(self):
        """Retorna um resumo das soluções da ocorrência"""
        solucoes = []
        if self.evadiu_se:
            solucoes.append('Evadiu-se do local')
        if self.samu_acionado:
            solucoes.append('SAMU acionado')
        if self.conduzido_delegacia:
            solucoes.append('Conduzido à Delegacia')
        return ', '.join(solucoes) if solucoes else 'Nenhuma informada'


class PessoaEnvolvida(models.Model):
    """
    Modelo para armazenar pessoas envolvidas na ocorrência
    """
    
    TIPO_PESSOA_CHOICES = [
        ('acusado', 'Acusado'),
        ('vitima', 'Vítima'),
        ('testemunha', 'Testemunha'),
    ]
    
    relatorio = models.ForeignKey(
        RelatorioAnalitico,
        on_delete=models.CASCADE,
        related_name='pessoas',
        verbose_name='Relatório'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_PESSOA_CHOICES,
        verbose_name='Tipo'
    )
    
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome completo'
    )
    
    cpf = models.CharField(
        max_length=14,
        verbose_name='CPF',
        blank=True,
        null=True,
        help_text='Formato: 000.000.000-00'
    )
    
    rg = models.CharField(
        max_length=20,
        verbose_name='RG',
        blank=True,
        null=True
    )
    
    endereco = models.TextField(
        verbose_name='Endereço',
        blank=True,
        null=True
    )
    
    nome_mae = models.CharField(
        max_length=200,
        verbose_name='Nome da mãe',
        blank=True,
        null=True
    )
    
    # Informações adicionais (opcionais)
    telefone = models.CharField(
        max_length=20,
        verbose_name='Telefone',
        blank=True,
        null=True
    )
    
    data_nascimento = models.DateField(
        verbose_name='Data de nascimento',
        blank=True,
        null=True
    )
    
    observacoes = models.TextField(
        verbose_name='Observações',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'Pessoa Envolvida'
        verbose_name_plural = 'Pessoas Envolvidas'
        ordering = ['tipo', 'nome']
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nome}"
    
    def save(self, *args, **kwargs):
        # Limpar CPF (remover pontos e traços)
        if self.cpf:
            self.cpf = self.cpf.replace('.', '').replace('-', '')
        super().save(*args, **kwargs)


class NumeroRelatorio(models.Model):
    """
    Modelo para controlar a numeração automática dos relatórios
    """
    ano = models.IntegerField(verbose_name='Ano', unique=True)
    ultimo_numero = models.IntegerField(
        default=0,
        verbose_name='Último número utilizado'
    )
    
    class Meta:
        verbose_name = 'Controle de Numeração'
        verbose_name_plural = 'Controle de Numeração'
    
    def __str__(self):
        return f"{self.ano} - Nº {self.ultimo_numero}"
    
    @classmethod
    def get_proximo_numero(cls, ano=None):
        """
        Retorna o próximo número disponível para o ano
        """
        if ano is None:
            ano = timezone.now().year
        
        controle, created = cls.objects.get_or_create(ano=ano)
        controle.ultimo_numero += 1
        controle.save()
        
        return f"{controle.ultimo_numero:04d}/{ano}"


class AnexoRelatorio(models.Model):
    """
    Modelo para anexar arquivos ao relatório (opcional)
    """
    relatorio = models.ForeignKey(
        RelatorioAnalitico,
        on_delete=models.CASCADE,
        related_name='anexos',
        verbose_name='Relatório'
    )
    
    arquivo = models.FileField(
        upload_to='relatorios/anexos/%Y/%m/',
        verbose_name='Arquivo'
    )
    
    descricao = models.CharField(
        max_length=200,
        verbose_name='Descrição',
        blank=True,
        null=True
    )
    
    data_upload = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de upload'
    )
    
    class Meta:
        verbose_name = 'Anexo do Relatório'
        verbose_name_plural = 'Anexos dos Relatórios'
    
    def __str__(self):
        return f"Anexo: {self.descricao or self.arquivo.name}"