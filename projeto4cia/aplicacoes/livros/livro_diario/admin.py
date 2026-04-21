# admin.py - versão simplificada
from django.contrib import admin
from .models import LivroDiarioRelatorio

@admin.register(LivroDiarioRelatorio)
class LivroDiarioRelatorioAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'data_criacao', 'data_escala']
    list_filter = ['data_criacao', 'usuario']  # Removeu 'finalizado'
    search_fields = ['usuario__username', 'conteudo_html']
    readonly_fields = ['data_criacao']