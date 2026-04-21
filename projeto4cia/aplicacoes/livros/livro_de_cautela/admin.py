from django.contrib import admin
from .models import Relatorio


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'policial',
        'tipo_alteracao',
        'data_criacao',
        'assinado_em',
    )
    list_filter = (
        'tipo_alteracao',
        'data_criacao',
        'assinado_em',
    )
    search_fields = (
        'id',
        'policial__nome_guerra',
        'policial__nome',
        'observacoes',
    )
    readonly_fields = (
        'data_criacao',
        'assinado_em',
        'assinatura_passou_preview',
        'assinatura_recebeu_preview',
    )

    fieldsets = (
        ('Informações do Relatório', {
            'fields': (
                'policial',
                'tipo_alteracao',
                'observacoes',
                'data_criacao',
            )
        }),
        ('Conteúdo HTML', {
            'fields': ('conteudo_html',)
        }),
        ('Assinaturas', {
            'fields': (
                'assinatura_passou',
                'assinatura_passou_preview',
                'assinatura_recebeu',
                'assinatura_recebeu_preview',
                'assinado_em',
            )
        }),
    )

    def assinatura_passou_preview(self, obj):
        if obj.assinatura_passou:
            return admin.utils.html.format_html(
                '<img src="{}" width="200" style="border:1px solid #ccc;" />',
                obj.assinatura_passou.url
            )
        return "Sem assinatura"

    assinatura_passou_preview.short_description = "Prévia assinatura (quem passou)"

    def assinatura_recebeu_preview(self, obj):
        if obj.assinatura_recebeu:
            return admin.utils.html.format_html(
                '<img src="{}" width="200" style="border:1px solid #ccc;" />',
                obj.assinatura_recebeu.url
            )
        return "Sem assinatura"

    assinatura_recebeu_preview.short_description = "Prévia assinatura (quem recebeu)"