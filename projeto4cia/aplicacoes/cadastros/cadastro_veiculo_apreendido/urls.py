# aplicacoes/cadastros/cadastro_veiculo_apreendido/urls.py
from django.urls import path
from . import views

app_name = 'cadastro_veiculo_apreendido'

urlpatterns = [
    path('', views.lista_veiculos, name='lista'),
    path('novo/', views.novo_veiculo, name='novo'),
    path('editar/<int:pk>/', views.editar_veiculo, name='editar'),
    path('excluir/<int:pk>/', views.excluir_veiculo, name='excluir'),
    path('devolver/<int:pk>/', views.devolver_veiculo, name='devolver'),
    path('devolucao/print/<int:pk>/', views.imprimir_devolucao, name='imprimir_devolucao'),
]