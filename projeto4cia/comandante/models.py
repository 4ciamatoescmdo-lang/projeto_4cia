from django.db import models
from django.contrib.auth.models import User

class Comandante(models.Model):
    PATENTE_CHOICES = [
        ('CAP', 'Capitão'),
        ('MAJ', 'Major'),
        ('TC', 'Tenente Coronel'),
        ('CEL', 'Coronel'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='comandante')
    nome = models.CharField('Nome', max_length=200)
    patente = models.CharField('Patente', max_length=20, choices=PATENTE_CHOICES)
    data_nomeacao = models.DateField('Data de Nomeação')
    observacoes = models.TextField('Observações', blank=True)
    
    # ADICIONAR ESTES CAMPOS
    ativo = models.BooleanField('Ativo?', default=True)
    assinatura = models.ImageField(
        'Assinatura', 
        upload_to='assinaturas/comandantes/', 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = 'Comandante'
        verbose_name_plural = 'Comandantes'
    
    def __str__(self):
        return f'{self.get_patente_display()} {self.nome}'