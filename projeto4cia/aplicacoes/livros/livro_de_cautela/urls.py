from django.urls import path
from . import views

app_name = 'livro_de_cautela'

urlpatterns = [
    path('cautela/', views.lista_cautela, name='lista_cautela'),
    path('gerar-relatorio/', views.gerar_relatorio, name='gerar_relatorio'),
    path('relatorio/<int:relatorio_id>/', views.visualizar_relatorio, name='visualizar_relatorio'),
    path('listar-relatorios/', views.listar_relatorios, name='listar_relatorios'),
    path('salvar-relatorio/', views.salvar_relatorio, name='salvar_relatorio'),
    path('salvar-assinaturas/<int:relatorio_id>/', views.salvar_assinaturas, name='salvar_assinaturas'),  # NOVA URL
    path('assinaturas/<int:relatorio_id>/', views.pagina_assinaturas, name='pagina_assinaturas'),
]