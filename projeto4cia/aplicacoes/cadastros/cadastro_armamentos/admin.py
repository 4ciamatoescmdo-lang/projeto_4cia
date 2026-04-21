from django.contrib import admin
from .models import Armamento

@admin.register(Armamento)
class ArmamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_serie', 'tipo', 'marca', 'modelo', 'calibre', 'status', 'criado_em')
    list_filter = ('status', 'tipo', 'calibre', 'ativo')
    search_fields = ('numero_serie', 'patrimonio', 'registro', 'marca', 'modelo')
    list_editable = ('status',)
    list_per_page = 50