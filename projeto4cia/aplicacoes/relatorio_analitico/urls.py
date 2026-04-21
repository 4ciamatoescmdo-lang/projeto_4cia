from django.urls import path
from . import views

app_name = 'relatorio_analitico'

urlpatterns = [
    path('', views.form_relatorio, name='form_relatorio'),
    path('salvar/', views.salvar_relatorio, name='salvar_relatorio'),
    path('lista/', views.lista_relatorios, name='lista_relatorios'),
    path('visualizar/<int:pk>/', views.visualizar_relatorio, name='visualizar_relatorio'),
    path('editar/<int:pk>/', views.editar_relatorio, name='editar_relatorio'),
    path('excluir/<int:pk>/', views.excluir_relatorio, name='excluir_relatorio'),
    path('imprimir/<int:pk>/', views.imprimir_relatorio, name='imprimir_relatorio'),
]