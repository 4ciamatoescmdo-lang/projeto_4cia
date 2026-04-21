from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Policial(models.Model):
    PATENTE_CHOICES = [
        ('SD PM', 'SD PM'),
        ('CB PM', 'CB PM'),
        ('3º SGT PM', '3º SGT PM'),
        ('2º SGT PM', '2º SGT PM'),
        ('1º SGT PM', '1º SGT PM'),
        ('ST PM', 'ST PM'),
        ('2º TEN QOPM', '2º TEN QOPM'),
        ('1º TEN QOPM', '1º TEN QOPM'),
        ('CAP QOPM', 'CAP QOPM'),
        ('MAJ QOPM', 'MAJ QOPM'),
        ('TC QOPM', 'TC QOPM'),
        ('CEL', 'CEL'),
    ]
    
    # Mapeamento para ordenação hierárquica (maior valor = maior patente)
    PATENTE_ORDER = {
        'SD PM': 1,
        'CB PM': 2,
        '3º SGT PM': 3,
        '2º SGT PM': 4,
        '1º SGT PM': 5,
        'ST PM': 6,
        '2º TEN QOPM': 7,
        '1º TEN QOPM': 8,
        'CAP QOPM': 9,
        'MAJ QOPM': 10,
        'TC QOPM': 11,
        'CEL': 12,
    }

    # Relacionamento com User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='policial')

    nome_completo = models.CharField('Nome Completo', max_length=200)
    data_de_nascimento = models.DateField('Data de Nascimento', null=True, blank=True, help_text='Data de nascimento')
    nome_guerra = models.CharField('Nome de Guerra', max_length=50)
    patente = models.CharField('Patente', max_length=20, choices=PATENTE_CHOICES)
    data_promocao = models.DateField('Data da Promoção', null=True, blank=True, help_text='Data da última promoção')
    barra = models.IntegerField('Ano de Entrada', null=True, blank=True)
    numero_barra = models.CharField('Número da Barra', max_length=20, blank=True)
    matricula = models.CharField('Matrícula', max_length=20, unique=True)
    cpf = models.CharField('CPF', max_length=14, unique=True)
    telefone = models.CharField('Telefone', max_length=20)
    ativo = models.BooleanField('Ativo?', default=True)
    observacoes = models.TextField('Observações', blank=True)
    
    # CAMPO PARA ASSINATURA EM PNG
    assinatura = models.ImageField(
        'Assinatura', 
        upload_to='assinaturas/policiais/', 
        blank=True, 
        null=True,
        help_text='Upload da imagem da assinatura do policial (formato PNG)'
    )
    
    # CAMPO PARA ORDENAÇÃO HIERÁRQUICA DAS PATENTES
    ordem_patente = models.IntegerField(
        'Ordem da Patente', 
        editable=False, 
        db_index=True, 
        default=0,
        help_text='Campo automático para ordenação hierárquica das patentes'
    )
    
    # Datas automáticas
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Policial'
        verbose_name_plural = 'Policiais'
        # Ordenação: patente maior primeiro (ordem decrescente), depois barra (mais recente primeiro), depois número_barra
        ordering = ['-ordem_patente','data_promocao', 'barra', 'numero_barra' ]
    
    def save(self, *args, **kwargs):
        # Preenche automaticamente o campo ordem_patente baseado na patente
        self.ordem_patente = self.PATENTE_ORDER.get(self.patente, 0)
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.barra:
            # Converte o ano para string e pega os dois últimos dígitos
            ano_str = str(self.barra)
            ano_formatado = ano_str[-2:] if len(ano_str) >= 2 else ano_str
            ano_texto = ano_formatado
        else:
            ano_texto = "??"
        
        return f'{self.get_patente_display()} {self.numero_barra}/{ano_texto} {self.nome_guerra}'


# SIGNAL: Cria usuário automaticamente quando um policial é cadastrado
@receiver(post_save, sender=Policial)
def criar_usuario_policial(sender, instance, created, **kwargs):
    if created and not instance.user:
        # Cria username baseado no nome_guerra (sem espaços, minúsculo)
        username_base = instance.nome_guerra.lower().replace(' ', '_')
        username = username_base
        
        # Garante que o username é único
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1
        
        # Cria o usuário
        user = User.objects.create_user(
            username=username,
            first_name=instance.nome_guerra,
            password='mudar123'  # Senha padrão, o policial deve alterar depois
        )
        
        # Vincula o usuário ao policial
        instance.user = user
        instance.save(update_fields=['user'])