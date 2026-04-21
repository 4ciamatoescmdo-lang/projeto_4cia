# aplicacoes/escala_diaria/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
import json
import logging

from .models import EscalaGerada, PolicialEscalaExterno, Permuta, Dispensa
from .forms import EscalaForm, PolicialExternoForm, PermutaForm, DispensaForm
from .utils import processar_permutas_da_escala  # NOVO IMPORT
from aplicacoes.cadastros.cadastro_policiais.models import Policial
from aplicacoes.cadastros.cadastro_vtrs.models import Viatura
from aplicacoes.cadastros.cadastro_comandante.models import Comandante


logger = logging.getLogger(__name__)

def gerar_texto_escala(data_escala, permanencia, policiais_externos, permutas, dispensas):
    """Função auxiliar para gerar o texto formatado da escala"""
    
    # Cabeçalho fixo
    texto = """ESTADO DO MARANHÃO
POLÍCIA MILITAR DO ESTADO DO MARANHÃO
CPI/CPAI-4/4a. CIA /11ºBPM/ MATÕES-MA
                                                   
"""
    # Data
    dias_semana = ['SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA', 
                   'SEXTA-FEIRA', 'SÁBADO', 'DOMINGO']
    dia_semana = dias_semana[data_escala.weekday()]
    texto += f"ESCALA DE SERVIÇO DO DIA {data_escala.strftime('%d/%m/%Y')} ({dia_semana}).\n\n"
    
    # Serviço de 24hs - Permanência
    texto += "SERVIÇO DE 24 HS:\n"
    texto += "PERMANÊNCIA:\n"
    if permanencia:
        texto += f"- {permanencia}\n"
    else:
        texto += "- NÃO INFORMADO\n"
    texto += "\n"
    
    # Serviço Externo
    if policiais_externos:
        texto += "SERVIÇO EXTERNO:\n"
        
        # Agrupar policiais por viatura
        viaturas_dict = {}
        for pe in policiais_externos:
            viatura_prefixo = pe['viatura'].prefixo
            if viatura_prefixo not in viaturas_dict:
                viaturas_dict[viatura_prefixo] = []
            viaturas_dict[viatura_prefixo].append(pe)
        
        # Escrever cada viatura e seus policiais
        for viatura_prefixo, policiais in viaturas_dict.items():
            texto += f" VTR  {viatura_prefixo}:\n"
            for pe in policiais:
                # CORRIGIDO: Acessar a função corretamente
                funcao = dict(EscalaGerada.FUNCAO_CHOICES)[pe['funcao']]
                texto += f"- {pe['policial']} - {funcao};\n"
        texto += "\n"
    
    # Permutas
    if permutas:
        texto += "PERMUTA DE SERVIÇO C/A\n"
        texto += "* PERMUTAS NO SERVIÇO DE 24 H\n"
        texto += "ENTRE:\n"
        for p in permutas:
            tipo = dict(EscalaGerada.TIPO_PERMUTA_CHOICES)[p['tipo']]
            texto += f"- {p['policial_a']} E {p['policial_b']} ({tipo});\n"
    else:
        texto += "PERMUTA DE SERVIÇO S/A\n"
    texto += "\n"
    
    # Dispensas e Faltas
    if dispensas:
        texto += "DISPENSAS E FALTAS C/A:\n"
        for d in dispensas:
            motivo = dict(EscalaGerada.MOTIVO_DISPENSA_CHOICES)[d['motivo']]
            tipo = dict(EscalaGerada.TIPO_DISPENSA_CHOICES)[d['tipo']]
            texto += f"- {d['policial']} - {motivo} ({tipo})\n"
    else:
        texto += "DISPENSAS E FALTAS: S/A\n"
    texto += "\n"
    
    # Rodapé
    texto += f"MATÕES-MA, {data_escala.strftime('%d DE %B DE %Y').upper()}."
    
    return texto

@login_required
def nova_escala(request):
    """View para criar uma nova escala"""
    comandante = Comandante.objects.filter(ativo=True).order_by('-data_nomeacao').first()
    # CORRIGIDO: Use os campos corretos do modelo Policial
    context = {
        'policiais': Policial.objects.filter(ativo=True).order_by('patente', 'nome_guerra'),
        'viaturas': Viatura.objects.filter(ativo=True).order_by('prefixo'),
        'tipos_permuta': EscalaGerada.TIPO_PERMUTA_CHOICES,
        'motivos_dispensa': EscalaGerada.MOTIVO_DISPENSA_CHOICES,
        'funcoes': EscalaGerada.FUNCAO_CHOICES,
        'comandante': comandante,  # ADICIONE ESTA LINHA
    }
    
    if request.method == 'POST':
        # Processar os dados do formulário
        data_escala = datetime.strptime(request.POST.get('data_escala'), '%Y-%m-%d').date()
        
        # Permanência
        permanencia_id = request.POST.get('permanencia')
        permanencia = Policial.objects.get(id=permanencia_id) if permanencia_id else None
        
        # Processar policiais externos
        policiais_externos = []
        indices = request.POST.getlist('externo_indice')
        for i in range(len(indices)):
            policial_id = request.POST.get(f'externo_policial_{i}')
            viatura_id = request.POST.get(f'externo_viatura_{i}')
            funcao = request.POST.get(f'externo_funcao_{i}')
            
            if policial_id and viatura_id and funcao:
                policiais_externos.append({
                    'policial': Policial.objects.get(id=policial_id),
                    'viatura': Viatura.objects.get(id=viatura_id),
                    'funcao': funcao
                })
        
        # Processar permutas
        permutas = []
        indices_permuta = request.POST.getlist('permuta_indice')
        for i in range(len(indices_permuta)):
            policial_a_id = request.POST.get(f'permuta_policial_a_{i}')
            policial_b_id = request.POST.get(f'permuta_policial_b_{i}')
            tipo = request.POST.get(f'permuta_tipo_{i}')
            
            if policial_a_id and policial_b_id and tipo:
                permutas.append({
                    'policial_a': Policial.objects.get(id=policial_a_id),
                    'policial_b': Policial.objects.get(id=policial_b_id),
                    'tipo': tipo
                })
        
        # Processar dispensas
        dispensas = []
        indices_dispensa = request.POST.getlist('dispensa_indice')
        for i in range(len(indices_dispensa)):
            policial_id = request.POST.get(f'dispensa_policial_{i}')
            motivo = request.POST.get(f'dispensa_motivo_{i}')
            tipo = request.POST.get(f'dispensa_tipo_{i}')
            
            if policial_id and motivo and tipo:
                dispensas.append({
                    'policial': Policial.objects.get(id=policial_id),
                    'motivo': motivo,
                    'tipo': tipo
                })
        
        # Gerar o texto
        texto_gerado = gerar_texto_escala(
            data_escala, 
            permanencia, 
            policiais_externos, 
            permutas, 
            dispensas
        )
        
        # Salvar no banco de dados
        escala = EscalaGerada.objects.create(
            data_escala=data_escala,
            criado_por=request.user,
            permanencia=permanencia,
            texto_gerado=texto_gerado
        )
        
        # Salvar relacionamentos
        for i, pe in enumerate(policiais_externos):
            PolicialEscalaExterno.objects.create(
                escala=escala,
                policial=pe['policial'],
                viatura=pe['viatura'],
                funcao=pe['funcao'],
                ordem=i
            )
        
        # Lista para armazenar objetos Permuta criados
        permutas_criadas = []
        for i, p in enumerate(permutas):
            permuta_obj = Permuta.objects.create(
                escala=escala,
                policial_a=p['policial_a'],
                policial_b=p['policial_b'],
                tipo=p['tipo'],
                ordem=i
            )
            permutas_criadas.append(permuta_obj)
        
        for i, d in enumerate(dispensas):
            Dispensa.objects.create(
                escala=escala,
                policial=d['policial'],
                motivo=d['motivo'],
                tipo=d['tipo'],
                ordem=i
            )
        
        # =====================================================
        # NOVO: GERAR HTMLs DAS PERMUTAS AUTOMATICAMENTE
        # =====================================================
        if permutas_criadas:
            try:
                resultados_permutas = processar_permutas_da_escala(escala, permutas_criadas)
                
                # Adicionar mensagem de sucesso
                if resultados_permutas['gerados'] > 0:
                    messages.success(
                        request, 
                        f'✓ Escala gerada com sucesso! {resultados_permutas["gerados"]} '
                        f'formulários de permuta foram gerados automaticamente.'
                    )
                    
                    # Log dos arquivos gerados (opcional)
                    for arquivo in resultados_permutas['arquivos']:
                        logger.info(f"Permuta HTML: {arquivo['caminho']}")
                
                if resultados_permutas['erros'] > 0:
                    messages.warning(
                        request,
                        f'Atenção: {resultados_permutas["erros"]} permuta(s) não puderam ser processadas.'
                    )
                    
            except Exception as e:
                logger.error(f"Erro ao processar permutas da escala {escala.id}: {str(e)}")
                messages.warning(
                    request,
                    'Escala gerada, mas houve um erro ao gerar os formulários de permuta.'
                )
        # =====================================================
        
        # Retornar para a página com o texto gerado
        context['texto_gerado'] = texto_gerado
        context['escala_id'] = escala.id
        context['data_escala'] = data_escala
        context['permanencia'] = permanencia
        context['policiais_externos'] = policiais_externos
        context['permutas'] = permutas
        context['dispensas'] = dispensas
        
        return render(request, 'escala_diaria/resultado.html', context)
    
    # GET request - mostrar formulário vazio
    context['data_hoje'] = timezone.now().date()
    return render(request, 'escala_diaria/nova_escala.html', context)

@login_required
def historico_escalas(request):
    """View para listar escalas anteriores"""
    escalas = EscalaGerada.objects.all().order_by('-data_escala', '-data_criacao')
    return render(request, 'escala_diaria/historico.html', {'escalas': escalas})

@login_required
def visualizar_escala(request, escala_id):
    """View para visualizar uma escala específica"""
    escala = EscalaGerada.objects.get(id=escala_id)
    policiais_externos = escala.policiais_externos.all().select_related('policial', 'viatura')
    permutas = escala.permutas.all().select_related('policial_a', 'policial_b')
    dispensas = escala.dispensas.all().select_related('policial')
    
    context = {
        'escala': escala,
        'policiais_externos': policiais_externos,
        'permutas': permutas,
        'dispensas': dispensas,
        'texto_gerado': escala.texto_gerado,
    }
    return render(request, 'escala_diaria/resultado.html', context)


import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def listar_arquivos_escala(request):
    """Lista todos os arquivos HTML de permutas gerados"""
    pasta_permutas = os.path.join(settings.MEDIA_ROOT, 'permutas_escala')
    arquivos = []
    
    if os.path.exists(pasta_permutas):
        for arquivo in sorted(os.listdir(pasta_permutas), reverse=True):
            if arquivo.endswith('.html'):
                arquivos.append({
                    'nome': arquivo,
                    'caminho': os.path.join(settings.MEDIA_URL, 'permutas_escala', arquivo),
                    'data': os.path.getmtime(os.path.join(pasta_permutas, arquivo))
                })
    
    return render(request, 'escala_diaria/lista_escalas.html', {'arquivos': arquivos})