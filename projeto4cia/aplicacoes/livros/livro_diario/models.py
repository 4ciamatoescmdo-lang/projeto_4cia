from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LivroDiarioRelatorio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_escala = models.DateField(default=timezone.now)
    conteudo_html = models.TextField()  # HTML imutável
    
    class Meta:
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Relatório {self.id} - {self.data_escala}"