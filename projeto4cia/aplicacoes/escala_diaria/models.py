# aplicacoes/escala_diaria/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Importe os modelos existentes com os nomes corretos
from aplicacoes.cadastros.cadastro_policiais.models import Policial
from aplicacoes.cadastros.cadastro_vtrs.models import Viatura  # CORRIGIDO: Viatura ao invés de Vtr


class EscalaGerada(models.Model):
    """Modelo principal para salvar as escalas geradas"""
    
    TIPO_PERMUTA_CHOICES = [
        ('24HS', '24hs'),
        ('1_QTU', '1 QTU'),
        ('2_QTU', '2 QTU'),
        ('1_GIRO', '1 GIRO'),
        ('2_GIRO', '2 GIRO'),
    ]
    
    TIPO_DISPENSA_CHOICES = [
        ('24HS', '24hs'),
        ('1_QTU', '1 QTU'),
        ('2_QTU', '2 QTU'),
        ('1_GIRO', '1 GIRO'),
        ('2_GIRO', '2 GIRO'),
    ]
    
    MOTIVO_DISPENSA_CHOICES = [
        ('FOLGA', 'Folga'),
        ('LICENCA_SAUDE', 'Licença Saúde'),
        ('LUTO', 'Luto'),
        ('CASAMENTO', 'Casamento'),
        ('TREINAMENTO', 'Treinamento'),
        ('SERVICO_ADMIN', 'Serviço Administrativo'),
        ('DISPENSADO_CMD', 'Dispensado pelo Cmd da Cia'),
        ('ARMA_FOGO', 'Dispensado por Arma de Fogo'),
        ('REFORCO_POLICIAL', 'Dispensado por Reforço Policial'),
        ('OUTROS', 'Outros'),
    ]
    
    FUNCAO_CHOICES = [
        ('CMT_VTR', 'CMT DA VTR'),
        ('MOTORISTA', 'MOT'),
        ('PATRULHEIRO', 'PAT'),
        ('MOTOCICLISTA', 'MOTOCICLISTA'),
    ]
    
    data_escala = models.DateField(default=timezone.now, verbose_name="Data da Escala")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Criado por")
    
    # Permanência
    permanencia = models.ForeignKey(
        Policial, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='escalas_permanencia',
        verbose_name="Policial na Permanência"
    )
    
    # Texto completo gerado
    texto_gerado = models.TextField(verbose_name="Texto da Escala")
    
    class Meta:
        verbose_name = "Escala Gerada"
        verbose_name_plural = "Escalas Geradas"
        ordering = ['-data_escala', '-data_criacao']
    
    def __str__(self):
        return f"Escala do dia {self.data_escala.strftime('%d/%m/%Y')}"


class PolicialEscalaExterno(models.Model):
    """Modelo para os policiais no serviço externo"""
    escala = models.ForeignKey(EscalaGerada, on_delete=models.CASCADE, related_name='policiais_externos')
    policial = models.ForeignKey(Policial, on_delete=models.SET_NULL, null=True)
    viatura = models.ForeignKey(
        Viatura,  # CORRIGIDO: Agora é Viatura
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Viatura"
    )
    funcao = models.CharField(max_length=20, choices=EscalaGerada.FUNCAO_CHOICES, verbose_name="Função")
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição")
    
    class Meta:
        ordering = ['ordem']
        verbose_name = "Policial no Serviço Externo"
        verbose_name_plural = "Policiais no Serviço Externo"
    
    def __str__(self):
        return f"{self.policial} - {self.viatura.prefixo if self.viatura else 'VTR não informada'} - {self.get_funcao_display()}"


class Permuta(models.Model):
    """Modelo para as permutas"""
    escala = models.ForeignKey(EscalaGerada, on_delete=models.CASCADE, related_name='permutas')
    policial_a = models.ForeignKey(
        Policial, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='permutas_como_a',
        verbose_name="Policial A"
    )
    policial_b = models.ForeignKey(
        Policial, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='permutas_como_b',
        verbose_name="Policial B"
    )
    tipo = models.CharField(max_length=20, choices=EscalaGerada.TIPO_PERMUTA_CHOICES, verbose_name="Tipo")
    ordem = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = "Permuta"
        verbose_name_plural = "Permutas"
    
    def __str__(self):
        return f"{self.policial_a} x {self.policial_b} ({self.get_tipo_display()})"


class Dispensa(models.Model):
    """Modelo para as dispensas/faltas"""
    escala = models.ForeignKey(EscalaGerada, on_delete=models.CASCADE, related_name='dispensas')
    policial = models.ForeignKey(
        Policial, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Policial"
    )
    motivo = models.CharField(max_length=50, choices=EscalaGerada.MOTIVO_DISPENSA_CHOICES, verbose_name="Motivo")
    tipo = models.CharField(max_length=20, choices=EscalaGerada.TIPO_DISPENSA_CHOICES, verbose_name="Tipo")
    ordem = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = "Dispensa"
        verbose_name_plural = "Dispensas"
    
    def __str__(self):
        return f"{self.policial} - {self.get_motivo_display()} ({self.get_tipo_display()})"