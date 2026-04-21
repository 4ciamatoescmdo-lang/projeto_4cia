from django.contrib import admin
from .models import Equipamento

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'status', 'categoria', 'quantidade', 'criado_em')
    list_filter = ('status', 'categoria', 'ativo')
    search_fields = ('nome', 'patrimonio', 'numero_serie')
    list_editable = ('status',)  # permite editar status direto na lista