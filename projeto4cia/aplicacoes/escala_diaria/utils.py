# aplicacoes/escala_diaria/utils.py
import os
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from aplicacoes.cadastros.cadastro_comandante.models import Comandante
import logging

logger = logging.getLogger(__name__)

def get_graduacao_display(patente):
    """Converte a sigla da patente para o texto completo"""
    patentes = {
        'SD': 'SOLDADO',
        'CB': 'CABO',
        'SGT': 'SARGENTO',
        'ST': 'SUB TENENTE',
        'TEN': 'TENENTE',
        'CAP': 'CAPITÃO',
        'MAJ': 'MAJOR',
        'TC': 'TENENTE CORONEL',
        'CEL': 'CORONEL',
    }
    return patentes.get(patente, patente)

def get_assinatura_path(assinatura_field):
    """Retorna o caminho absoluto da imagem de assinatura"""
    if assinatura_field and hasattr(assinatura_field, 'path'):
        if os.path.exists(assinatura_field.path):
            # Converter caminho absoluto para URL
            return f"{settings.MEDIA_URL}{assinatura_field.name}"
    return None

def gerar_html_permuta(permuta, escala, data_servico=None):

    comandante = Comandante.objects.filter(ativo=True).order_by('-data_nomeacao').first()
    assinatura_comandante = get_assinatura_path(comandante.assinatura) if comandante else None

    if data_servico is None:
        data_servico = escala.data_escala
    
    # Calcular próximo dia
    data_proximo_dia = data_servico + timedelta(days=1)
    
    # Buscar dados dos policiais
    policial_a = permuta.policial_a
    policial_b = permuta.policial_b
    
    # Adicionar campo graduacao_texto para exibição
    policial_a.graduacao = get_graduacao_display(policial_a.patente)
    policial_b.graduacao = get_graduacao_display(policial_b.patente)
    
    # Buscar assinaturas
    assinatura_policial_a = get_assinatura_path(policial_a.assinatura)
    assinatura_policial_b = get_assinatura_path(policial_b.assinatura)
    
    # Buscar comandante ativo
    comandante = Comandante.objects.filter(ativo=True).first()
    assinatura_comandante = get_assinatura_path(comandante.assinatura) if comandante else None
    
    # Contexto para o template
    context = {
        'policial_a': policial_a,
        'policial_b': policial_b,
        'data_servico': data_servico,
        'data_proximo_dia': data_proximo_dia,
        'data_emissao': timezone.now().date(),
        'assinatura_policial_a': assinatura_policial_a,
        'assinatura_policial_b': assinatura_policial_b,
        'assinatura_comandante': assinatura_comandante,
        'tipo_permuta': permuta.get_tipo_display(),
        'escala_id': escala.id,
        'comandante': comandante,
    }
    
    # Renderizar template
    html_content = render_to_string('escala_diaria/permuta_template.html', context)
    
    return html_content

def salvar_html_permuta(html_content, escala_id, policial_a_matricula, data_servico):
    """
    Salva o HTML da permuta em um arquivo
    
    Args:
        html_content: Conteúdo HTML
        escala_id: ID da escala
        policial_a_matricula: Matrícula do policial solicitante
        data_servico: Data do serviço
    
    Returns:
        str: Caminho do arquivo salvo
    """
    # Criar pasta se não existir
    pasta_permutas = os.path.join(settings.MEDIA_ROOT, 'permutas_escala')
    if not os.path.exists(pasta_permutas):
        os.makedirs(pasta_permutas)
    
    # Gerar nome do arquivo
    data_str = data_servico.strftime('%Y%m%d')
    nome_arquivo = f"permuta_escala_{escala_id}_{policial_a_matricula}_{data_str}.html"
    caminho_completo = os.path.join(pasta_permutas, nome_arquivo)
    
    # Salvar arquivo
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Retornar caminho relativo para exibição
    caminho_relativo = os.path.join(settings.MEDIA_URL, 'permutas_escala', nome_arquivo)
    
    logger.info(f"Permuta HTML gerada: {caminho_completo}")
    
    return caminho_relativo

def processar_permutas_da_escala(escala, permutas):
    """
    Processa todas as permutas de uma escala e gera os HTMLs
    
    Args:
        escala: Objeto EscalaGerada
        permutas: Lista de objetos Permuta
    
    Returns:
        dict: Estatísticas das permutas processadas
    """
    resultados = {
        'total': len(permutas),
        'gerados': 0,
        'erros': 0,
        'arquivos': []
    }
    
    for i, permuta in enumerate(permutas):
        try:
            # Gerar HTML
            html_content = gerar_html_permuta(permuta, escala)
            
            # Salvar arquivo
            caminho = salvar_html_permuta(
                html_content,
                escala.id,
                permuta.policial_a.matricula,
                escala.data_escala
            )
            
            resultados['gerados'] += 1
            resultados['arquivos'].append({
                'permuta_id': permuta.id,
                'caminho': caminho,
                'policial_a': str(permuta.policial_a),
                'policial_b': str(permuta.policial_b)
            })
            
        except Exception as e:
            resultados['erros'] += 1
            logger.error(f"Erro ao gerar HTML para permuta {permuta.id}: {str(e)}")
    
    return resultados