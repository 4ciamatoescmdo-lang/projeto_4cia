from django.db import models

class Comandante(models.Model):
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

    nome = models.CharField(max_length=100)
    nome_guerra = models.CharField('Nome de Guerra', max_length=50, blank=True)
    patente = models.CharField(max_length=20, choices=PATENTE_CHOICES)
    data_nomeacao = models.DateField()
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField('Ativo?', default=True)
    
    # CAMPO PARA ASSINATURA EM PNG
    assinatura = models.ImageField(
        'Assinatura', 
        upload_to='assinaturas/comandantes/', 
        blank=True, 
        null=True,
        help_text='Upload da imagem da assinatura do comandante (formato PNG)'
    )

    class Meta:
        ordering = ['-data_nomeacao']

    def __str__(self):
        return f"{self.get_patente_display()} {self.nome_guerra or self.nome}"
    
    def get_patente_display(self):
        return dict(self.PATENTE_CHOICES).get(self.patente, self.patente)