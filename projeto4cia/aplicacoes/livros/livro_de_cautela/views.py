from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json
import traceback
from django.template.loader import render_to_string
from django.urls import reverse
from aplicacoes.cadastros.cadastro_comandante.models import Comandante

# Importando os models de todas as aplicações de cadastro
from aplicacoes.cadastros.cadastro_armamentos.models import Armamento
from aplicacoes.cadastros.cadastro_policiais.models import Policial
from aplicacoes.cadastros.cadastro_municoes.models import Municao
from aplicacoes.cadastros.cadastro_equipamentos.models import Equipamento
from aplicacoes.cadastros.cadastro_eletronicos.models import Eletronico
from aplicacoes.cadastros.cadastro_vtrs.models import Viatura
from aplicacoes.cadastros.cadastro_veiculo_apreendido.models import VeiculoApreendido
from aplicacoes.cautela_e_descautela.cautela_armamento.models import ItemCautela

# Importe o modelo do arquivo correto
from .models import Relatorio

def lista_cautela(request):
    policial = Policial.objects.all()
    
    # ==============================================
    # CORREÇÃO: Filtrar itens disponíveis
    # ==============================================
    
    # IDs dos itens que estão cautelados e NÃO DEVOLVIDOS
    armamentos_cautelados_ids = ItemCautela.objects.filter(
        devolvido=False, 
        armamento__isnull=False
    ).values_list('armamento_id', flat=True).distinct()
    
    equipamentos_cautelados_ids = ItemCautela.objects.filter(
        devolvido=False, 
        equipamento__isnull=False
    ).values_list('equipamento_id', flat=True).distinct()
    
    # CORREÇÃO PARA MUNIÇÕES: Calcular quantidade disponível
    from django.db.models import Sum
    
    # Primeiro, buscar todas as munições
    todas_municoes = Municao.objects.all()
    
    # Criar uma lista com as quantidades atualizadas
    municoes_disponiveis = []
    for municao in todas_municoes:
        # Somar todas as quantidades cauteladas e não devolvidas desta munição
        total_cautelado = ItemCautela.objects.filter(
            devolvido=False,
            municao=municao
        ).aggregate(total=Sum('quantidade_municao'))['total'] or 0
        
        # Calcular quantidade disponível
        quantidade_disponivel = municao.quantidade - total_cautelado
        
        # Adicionar à lista com a quantidade atualizada
        municao.quantidade_disponivel = quantidade_disponivel
        municoes_disponiveis.append(municao)
    
    # Filtrar armamentos e equipamentos disponíveis
    armamentos_disponiveis = Armamento.objects.exclude(id__in=armamentos_cautelados_ids)
    equipamentos_disponiveis = Equipamento.objects.exclude(id__in=equipamentos_cautelados_ids)
    
    # Itens que NÃO têm relação no modelo ItemCautela (buscar todos)
    eletronicos_disponiveis = Eletronico.objects.all()
    viaturas_disponiveis = Viatura.objects.all()
    veiculos_apreendidos = VeiculoApreendido.objects.all()
    
    # TABELA 1: Itens AINDA CAUTELADOS (não devolvidos)
    itens_nao_devolvidos = ItemCautela.objects.filter(devolvido=False)
    
    # TABELA 2: Itens DESCAUTELADOS HOJE (das 00:00 até 23:59)
    hoje = datetime.now().date()
    data_inicio = datetime(hoje.year, hoje.month, hoje.day, 0, 0, 0)
    data_fim = datetime(hoje.year, hoje.month, hoje.day, 23, 59, 59)
    
    itens_devolvidos_hoje = ItemCautela.objects.filter(
        devolvido=True,
        data_devolucao_item__gte=data_inicio,
        data_devolucao_item__lte=data_fim
    )

    # DEBUG
    print("="*60)
    print("DEBUG - ITENS AINDA CAUTELADOS:")
    print(f"Total itens não devolvidos: {itens_nao_devolvidos.count()}")
    print(f"Total itens devolvidos hoje: {itens_devolvidos_hoje.count()}")
    print(f"Armamentos totais: {Armamento.objects.count()}")
    print(f"Armamentos cautelados: {armamentos_cautelados_ids.count()}")
    print(f"Armamentos disponíveis: {armamentos_disponiveis.count()}")
    print(f"Munições disponíveis (com quantidades atualizadas): {len(municoes_disponiveis)}")
    for m in municoes_disponiveis:
        print(f"  {m.calibre} - Disponível: {m.quantidade_disponivel} de {m.quantidade}")
    print("="*60)
    
    context = {
        'policial': policial,
        'armamentos_cautelados': armamentos_disponiveis,
        'municoes_cauteladas': municoes_disponiveis,  # CORRIGIDO - agora com quantidade atualizada
        'equipamentos_cautelados': equipamentos_disponiveis,
        'eletronicos_cautelados': eletronicos_disponiveis,
        'vtrs_cautelados': viaturas_disponiveis,
        'veiculos_apreendidos': veiculos_apreendidos,
        'itens_nao_devolvidos': itens_nao_devolvidos,
        'itens_devolvidos_hoje': itens_devolvidos_hoje,
    }
    
    return render(request, 'livro_de_cautela/lista_cautela.html', context)


def gerar_relatorio(request):
    try:
        data = json.loads(request.body.decode('utf-8'))        
        policial_id = data.get('policial_id')
        observacoes = data.get('observacoes', '')
        tipo_alteracao = data.get('tipo_alteracao', '')
        
        if not policial_id:
            return JsonResponse({
                "success": False,
                "message": "ID do policial não fornecido."
            }, status=400)
        
        if not tipo_alteracao:
            return JsonResponse({
                "success": False,
                "message": "Tipo de alteração não fornecido."
            }, status=400)
        
        # Buscar o policial substituto (quem vai receber)
        try:
            policial_substituto = Policial.objects.get(id=policial_id)
        except Policial.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Policial não encontrado."
            }, status=404)
        
        # Buscar o policial logado (quem está passando)
        if request.user.is_authenticated and hasattr(request.user, 'policial'):
            policial_passando = request.user.policial
        else:
            policial_passando = None
        
        # ==============================================
        # FILTRAGEM POR PERÍODO: das 8h do dia anterior até agora
        # ==============================================
        agora = datetime.now()
        
        # Data/hora de início: dia anterior às 8:00
        data_inicio = datetime(
            agora.year, agora.month, agora.day, 8, 0, 0
        ) - timedelta(days=1)
        
        # Data/hora de fim: agora (momento atual)
        data_fim = agora
        
        # Formatação para exibição
        data_anterior_str = data_inicio.strftime('%d/%m/%Y')
        data_hoje_str = agora.strftime('%d/%m/%Y')
        data_geracao = agora.strftime('%d/%m/%Y')
        
        # 1. BUSCAR TODOS OS ITENS NÃO DEVOLVIDOS (independente da data)
        itens_nao_devolvidos = ItemCautela.objects.filter(devolvido=False)
        
        # 2. BUSCAR ITENS DEVOLVIDOS NO PERÍODO (das 8h anterior até agora)
        itens_devolvidos_periodo = ItemCautela.objects.filter(
            devolvido=True,
            data_devolucao_item__gte=data_inicio,
            data_devolucao_item__lte=data_fim
        )
        
        # 3. COMBINAR OS ITENS
        itens_cautelados = itens_nao_devolvidos.union(itens_devolvidos_periodo)
        
        # DEBUG
        print("="*60)
        print(f"Período: {data_inicio.strftime('%d/%m/%Y %H:%M')} até {data_fim.strftime('%d/%m/%Y %H:%M')}")
        print(f"Total de itens não devolvidos: {itens_nao_devolvidos.count()}")
        print(f"Itens devolvidos no período: {itens_devolvidos_periodo.count()}")
        print(f"Total de itens no relatório: {itens_cautelados.count()}")
        print("="*60)
        
        # ==============================================
        # CORREÇÃO: Buscar apenas itens DISPONÍVEIS (não cautelados)
        # ==============================================
        
        # IDs dos itens que estão cautelados e NÃO DEVOLVIDOS
        armamentos_cautelados_ids = ItemCautela.objects.filter(
            devolvido=False, 
            armamento__isnull=False
        ).values_list('armamento_id', flat=True).distinct()
        
        equipamentos_cautelados_ids = ItemCautela.objects.filter(
            devolvido=False, 
            equipamento__isnull=False
        ).values_list('equipamento_id', flat=True).distinct()
        
        # Filtrar armamentos e equipamentos (excluir os cautelados)
        armamentos_disponiveis = Armamento.objects.exclude(id__in=armamentos_cautelados_ids)
        equipamentos_disponiveis = Equipamento.objects.exclude(id__in=equipamentos_cautelados_ids)
        
        # CORREÇÃO PARA MUNIÇÕES: Calcular quantidade disponível
        from django.db.models import Sum
        
        todas_municoes = Municao.objects.all()
        municoes_disponiveis = []
        for municao in todas_municoes:
            # Somar todas as quantidades cauteladas e não devolvidas desta munição
            total_cautelado = ItemCautela.objects.filter(
                devolvido=False,
                municao=municao
            ).aggregate(total=Sum('quantidade_municao'))['total'] or 0
            
            # Calcular quantidade disponível
            quantidade_disponivel = municao.quantidade - total_cautelado
            
            # Adicionar à lista com a quantidade atualizada
            municao.quantidade_disponivel = quantidade_disponivel
            municoes_disponiveis.append(municao)
        
        # Itens que NÃO têm relação no modelo ItemCautela (buscar todos)
        eletronicos_disponiveis = Eletronico.objects.all()
        viaturas_disponiveis = Viatura.objects.all()
        
        # Veículos apreendidos
        veiculos = VeiculoApreendido.objects.all()
        comandante = Comandante.objects.first()
        
        # DEBUG para mostrar quantos itens foram filtrados
        print(f"Armamentos totais: {Armamento.objects.count()}")
        print(f"Armamentos cautelados: {armamentos_cautelados_ids.count()}")
        print(f"Armamentos disponíveis: {armamentos_disponiveis.count()}")
        print(f"Equipamentos totais: {Equipamento.objects.count()}")
        print(f"Equipamentos cautelados: {equipamentos_cautelados_ids.count()}")
        print(f"Equipamentos disponíveis: {equipamentos_disponiveis.count()}")
        print(f"Munições disponíveis (com quantidades atualizadas): {len(municoes_disponiveis)}")
        for m in municoes_disponiveis:
            print(f"  {m.calibre} - Disponível: {m.quantidade_disponivel} de {m.quantidade}")
        print(f"Eletrônicos totais: {Eletronico.objects.count()}")
        print(f"Viaturas totais: {Viatura.objects.count()}")
        print("="*60)
        
        # Nome do policial logado
        if request.user.is_authenticated:
            policial_logado = request.user.first_name or request.user.username or "Usuário"
        else:
            policial_logado = "Não autenticado"
        
        # Renderizar o template do relatório
        html_content = render_to_string('livro_de_cautela/relatorio_cautela.html', {
            'policial_substituto': policial_substituto,
            'policial_passando': policial_passando,
            'policial_logado': policial_logado,
            'data_anterior': data_anterior_str,
            'data_hoje': data_hoje_str,
            'observacoes': observacoes,
            'armamentos_cautelados': armamentos_disponiveis,
            'municoes_cauteladas': municoes_disponiveis,  # CORRIGIDO
            'equipamentos_cautelados': equipamentos_disponiveis,
            'eletronicos_cautelados': eletronicos_disponiveis,
            'vtrs_cautelados': viaturas_disponiveis,
            'veiculos_apreendidos': veiculos,
            'data_geracao': data_geracao,
            'itens': itens_cautelados,
            'tipo_alteracao': tipo_alteracao,
            'total_nao_devolvidos': itens_nao_devolvidos.count(),
            'total_devolvidos_periodo': itens_devolvidos_periodo.count(),
            'comandante': comandante,
        })
        
        # Salvar o relatório
        relatorio = Relatorio.objects.create(
            conteudo_html=html_content,
            policial=policial_substituto,
            observacoes=observacoes,
            tipo_alteracao=tipo_alteracao
        )
        
        return JsonResponse({
            "success": True,
            "message": "Relatório gerado com sucesso.",
            "redirect_url": reverse('livro_de_cautela:visualizar_relatorio', args=[relatorio.id])
        })
        
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            "success": False,
            "message": f"Erro ao gerar relatório: {str(e)}"
        }, status=500)


def visualizar_relatorio(request, relatorio_id):
    relatorio = get_object_or_404(Relatorio, id=relatorio_id)
    return HttpResponse(relatorio.conteudo_html)


def listar_relatorios(request):
    relatorios = Relatorio.objects.all().order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(relatorios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'relatorios': page_obj,
    }
    return render(request, 'livro_de_cautela/listar_relatorios.html', context)


@require_POST
def salvar_relatorio(request):
    try:
        data = json.loads(request.body.decode('utf-8'))        
        html_content = data.get('conteudo_html', '')
        
        if not html_content:
            return JsonResponse({
                "success": False,
                "message": "Conteúdo do relatório não fornecido."
            }, status=400)
        
        relatorio = Relatorio.objects.create(conteudo_html=html_content)
        
        return JsonResponse({
            "success": True,
            "message": "Relatório salvo com sucesso.",
            "id": relatorio.id
        })
        
    except json.JSONDecodeError as e:
        return JsonResponse({
            "success": False,
            "message": f"Formato JSON inválido: {str(e)}"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Erro ao salvar relatório: {str(e)}"
        }, status=500)


from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import base64
from django.core.files.base import ContentFile
import os

@csrf_exempt
def salvar_assinaturas(request, relatorio_id):
    """View para salvar as assinaturas do relatório"""
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)
        
        relatorio = get_object_or_404(Relatorio, id=relatorio_id)
        
        data = json.loads(request.body.decode('utf-8'))
        
        # Processar assinatura de quem passou
        assinatura_passou_data = data.get('assinatura_passou')
        if assinatura_passou_data and assinatura_passou_data.startswith('data:image'):
            format, imgstr = assinatura_passou_data.split(';base64,')
            ext = format.split('/')[-1]
            assinatura_passou_file = ContentFile(base64.b64decode(imgstr), name=f'assinatura_passou_{relatorio_id}.{ext}')
            relatorio.assinatura_passou = assinatura_passou_file
        
        # Processar assinatura de quem recebeu
        assinatura_recebeu_data = data.get('assinatura_recebeu')
        if assinatura_recebeu_data and assinatura_recebeu_data.startswith('data:image'):
            format, imgstr = assinatura_recebeu_data.split(';base64,')
            ext = format.split('/')[-1]
            assinatura_recebeu_file = ContentFile(base64.b64decode(imgstr), name=f'assinatura_recebeu_{relatorio_id}.{ext}')
            relatorio.assinatura_recebeu = assinatura_recebeu_file
        
        relatorio.assinado_em = timezone.now()
        relatorio.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Assinaturas salvas com sucesso!',
            'redirect_url': reverse('livro_de_cautela:visualizar_relatorio', args=[relatorio.id])
        })
        
    except Exception as e:
        print(f"Erro ao salvar assinaturas: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Erro ao salvar assinaturas: {str(e)}'
        }, status=500)
    

def pagina_assinaturas(request, relatorio_id):
    """Exibe a página para assinar o relatório"""
    relatorio = get_object_or_404(Relatorio, id=relatorio_id)
    
    # Pegar o nome do policial logado
    if request.user.is_authenticated and hasattr(request.user, 'policial'):
        policial_logado = request.user.policial.nome_guerra
    else:
        policial_logado = request.user.first_name or request.user.username or "Usuário"
    
    context = {
        'relatorio': relatorio,
        'policial_logado': policial_logado,
    }
    
    return render(request, 'livro_de_cautela/assinaturas.html', context)