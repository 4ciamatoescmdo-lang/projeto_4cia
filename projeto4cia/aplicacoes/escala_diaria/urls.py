# aplicacoes/escala_diaria/urls.py
from django.urls import path
from . import views

app_name = 'escala_diaria'

urlpatterns = [
    path('nova/', views.nova_escala, name='nova_escala'),
    path('historico/', views.historico_escalas, name='historico'),
    path('visualizar/<int:escala_id>/', views.visualizar_escala, name='visualizar'),
    path('arquivos/', views.listar_arquivos_escala, name='listar_arquivos'),
]