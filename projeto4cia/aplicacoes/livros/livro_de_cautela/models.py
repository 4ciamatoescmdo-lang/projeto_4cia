from django.db import models

class Relatorio(models.Model):
    conteudo_html = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    policial = models.ForeignKey(
        'cadastro_policiais.Policial',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    observacoes = models.TextField(blank=True, null=True)
    tipo_alteracao = models.CharField(
        max_length=20, 
        choices=[
            ('COM ALTERAÇÃO', 'Com Alteração'),
            ('SEM ALTERAÇÃO', 'Sem Alteração')
        ],
        blank=True,
        null=True
    )
    
    # NOVOS CAMPOS: Assinaturas
    assinatura_passou = models.ImageField(
        'Assinatura Quem Passou',
        upload_to='relatorios/assinaturas/',
        blank=True,
        null=True
    )
    assinatura_recebeu = models.ImageField(
        'Assinatura Quem Recebeu',
        upload_to='relatorios/assinaturas/',
        blank=True,
        null=True
    )
    assinado_em = models.DateTimeField('Assinado em', blank=True, null=True)
    
    class Meta:
        ordering = ['-data_criacao']
        db_table = 'livro_de_cautela_relatorio'
    
    def __str__(self):
        return f"Relatório #{self.id} - {self.data_criacao.strftime('%d/%m/%Y %H:%M')}"