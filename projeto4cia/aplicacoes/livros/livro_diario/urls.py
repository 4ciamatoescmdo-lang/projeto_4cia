from django.urls import path
from . import views

app_name = 'livro_diario'

urlpatterns = [
    path('', views.livro_diario, name='livro_diario'),
    path('gerar/', views.gerar_relatorio, name='gerar_relatorio'),
    path('visualizar/<int:relatorio_id>/', views.visualizar_relatorio, name='visualizar_relatorio'),
    path('listar/', views.listar_relatorios, name='listar_relatorios'),
    path('gerar-relatorio-whatsapp/', views.gerar_relatorio_whatsapp, name='gerar_relatorio_whatsapp'),
]