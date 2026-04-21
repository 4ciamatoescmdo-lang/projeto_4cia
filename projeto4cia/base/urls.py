from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect 

urlpatterns = [
    path('', lambda request: redirect('autenticacao:login')), 
    path("admin/", admin.site.urls),
    path('cadastros/policiais/', include('aplicacoes.cadastros.cadastro_policiais.urls', namespace='cadastro_policiais')),
    path('auth/', include('aplicacoes.seguranca.autenticacao.urls', namespace='autenticacao')),
    path('cadastros/vtrs/', include('aplicacoes.cadastros.cadastro_vtrs.urls', namespace='cadastro_vtrs')),
    path('cadastros/armamentos/', include('aplicacoes.cadastros.cadastro_armamentos.urls', namespace='cadastro_armamentos')),
    path('cadastros/equipamentos/', include('aplicacoes.cadastros.cadastro_equipamentos.urls', namespace='cadastro_equipamentos')),
    path('cadastros/eletronicos/', include('aplicacoes.cadastros.cadastro_eletronicos.urls', namespace='cadastro_eletronicos')),
    path('cadastros/mobilia/', include('aplicacoes.cadastros.cadastro_mobilia.urls', namespace='cadastro_mobilia')),
    path('cautela_armamento/', include('aplicacoes.cautela_e_descautela.cautela_armamento.urls', namespace='cautela_armamento')),
    path('cadastros/municoes/', include('aplicacoes.cadastros.cadastro_municoes.urls', namespace='cadastro_municoes')),
    path('cadastros/comandante/', include('aplicacoes.cadastros.cadastro_comandante.urls', namespace='cadastro_comandante')),
    path('livros/diario/', include('aplicacoes.livros.livro_diario.urls', namespace='livro_diario')),
    path('livros/cautela/', include('aplicacoes.livros.livro_de_cautela.urls', namespace='livro_de_cautela')),
    path('cadastros/veiculo_apreendido/', include('aplicacoes.cadastros.cadastro_veiculo_apreendido.urls', namespace='cadastro_veiculo_apreendido')),
    path('escala/', include('aplicacoes.escala_diaria.urls')),
    path('relatorio-analitico/', include('aplicacoes.relatorio_analitico.urls', namespace='relatorio_analitico')),
    path('dashboard/', include('aplicacoes.dashboard.urls', namespace='dashboard')),
    # path('livro-diario/', include('aplicacoes.livros.livro_diario.urls')),
]

# Adicione isso no final do arquivo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)