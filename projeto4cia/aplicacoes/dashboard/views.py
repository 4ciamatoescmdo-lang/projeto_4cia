# dashboard/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Q, Avg, F, DecimalField
from django.db.models.functions import TruncMonth, TruncDate, ExtractMonth, ExtractYear
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator
import json

# Importações dos models existentes
from aplicacoes.cadastros.cadastro_policiais.models import Policial
from aplicacoes.cadastros.cadastro_armamentos.models import Armamento
from aplicacoes.cadastros.cadastro_vtrs.models import Viatura
from aplicacoes.cadastros.cadastro_municoes.models import Municao, MovimentacaoMunicao
from aplicacoes.cadastros.cadastro_eletronicos.models import Eletronico
from aplicacoes.cadastros.cadastro_equipamentos.models import Equipamento
from aplicacoes.cadastros.cadastro_mobilia.models import Mobilia
from aplicacoes.cadastros.cadastro_veiculo_apreendido.models import VeiculoApreendido
from aplicacoes.escala_diaria.models import EscalaGerada, PolicialEscalaExterno
from aplicacoes.relatorio_analitico.models import RelatorioAnalitico
from aplicacoes.cautela_e_descautela.cautela_armamento.models import Cautela, ItemCautela


@login_required
def dashboard_home(request):
    """Dashboard principal com todas as métricas"""
    
    # Dados para os cards principais
    context = {
        'total_policiais': Policial.objects.filter(ativo=True).count(),
        'total_armamentos': Armamento.objects.filter(ativo=True).count(),
        'total_viaturas': Viatura.objects.filter(ativo=True).count(),
        'total_apreendidos': VeiculoApreendido.objects.filter(devolvido=False).count(),
        'total_cautelas_ativas': Cautela.objects.filter(status='ATIVA').count(),
        'total_relatorios_mes': RelatorioAnalitico.objects.filter(
            data_ocorrencia__month=timezone.now().month,
            status='finalizado'
        ).count(),
    }
    
    # Gráfico de policiais por patente
    policiais_patente = Policial.objects.filter(ativo=True).values('patente').annotate(
        total=Count('id')
    ).order_by('patente')
    
    context['policiais_patente_labels'] = [item['patente'] for item in policiais_patente]
    context['policiais_patente_data'] = [item['total'] for item in policiais_patente]
    
    # Gráfico de armamentos por tipo
    armamentos_tipo = Armamento.objects.filter(ativo=True).values('tipo').annotate(
        total=Count('id')
    ).order_by('tipo')
    
    context['armamentos_tipo_labels'] = [item['tipo'] for item in armamentos_tipo]
    context['armamentos_tipo_data'] = [item['total'] for item in armamentos_tipo]
    
    # Status dos armamentos
    armamentos_status = Armamento.objects.filter(ativo=True).values('status').annotate(
        total=Count('id')
    )
    
    context['armamentos_status_labels'] = [item['status'] for item in armamentos_status]
    context['armamentos_status_data'] = [item['total'] for item in armamentos_status]
    
    # Viaturas por status
    viaturas_status = Viatura.objects.filter(ativo=True).values('status').annotate(
        total=Count('id')
    )
    
    context['viaturas_status_labels'] = [item['status'] for item in viaturas_status]
    context['viaturas_status_data'] = [item['total'] for item in viaturas_status]
    
    # Últimas cautelas
    context['ultimas_cautelas'] = Cautela.objects.filter(
        status='ATIVA'
    ).select_related('policial').order_by('-data_cautela')[:10]
    
    # Escalas recentes
    context['escalas_recentes'] = EscalaGerada.objects.select_related(
        'criado_por'
    ).order_by('-data_escala')[:5]
    
    # Relatórios recentes
    context['relatorios_recentes'] = RelatorioAnalitico.objects.filter(
        status='finalizado'
    ).order_by('-data_ocorrencia')[:10]
    
    # Munições com estoque baixo
    context['municoes_estoque_baixo'] = Municao.objects.filter(
        quantidade__lte=F('quantidade_minima')
    )[:10]
    
    # Equipamentos com estoque baixo
    context['equipamentos_estoque_baixo'] = Equipamento.objects.filter(
        quantidade__lte=F('quantidade_minima'),
        ativo=True
    )[:10]
    
    return render(request, 'dashboard/dashboard_home.html', context)


@login_required
def dashboard_armamentos(request):
    """Dashboard específica de armamentos"""
    
    context = {
        'total_armamentos': Armamento.objects.filter(ativo=True).count(),
        'disponiveis': Armamento.objects.filter(status='DISPONIVEL').count(),
        'em_uso': Armamento.objects.filter(status='EM_USO').count(),
        'manutencao': Armamento.objects.filter(status='MANUTENCAO').count(),
        'baixados': Armamento.objects.filter(status='BAIXADO').count(),
    }
    
    # Armamentos por tipo e status
    armamentos_detalhado = Armamento.objects.filter(ativo=True).values(
        'tipo', 'status'
    ).annotate(total=Count('id')).order_by('tipo', 'status')
    
    context['armamentos_detalhado'] = armamentos_detalhado
    
    # Últimos armamentos cadastrados
    context['ultimos_armamentos'] = Armamento.objects.filter(
        ativo=True
    ).order_by('-criado_em')[:15]
    
    # Armamentos por calibre
    armamentos_calibre = Armamento.objects.filter(ativo=True).values('calibre').annotate(
        total=Count('id')
    ).order_by('-total')
    
    context['armamentos_calibre_labels'] = [item['calibre'] for item in armamentos_calibre]
    context['armamentos_calibre_data'] = [item['total'] for item in armamentos_calibre]
    
    # Armamentos por marca
    armamentos_marca = Armamento.objects.filter(ativo=True).values('marca').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    context['armamentos_marca_labels'] = [item['marca'] for item in armamentos_marca]
    context['armamentos_marca_data'] = [item['total'] for item in armamentos_marca]
    
    return render(request, 'dashboard/dashboard_armamentos.html', context)


@login_required
def dashboard_policiais(request):
    """Dashboard específica de policiais"""
    
    context = {
        'total_policiais': Policial.objects.filter(ativo=True).count(),
        'policiais_ativos': Policial.objects.filter(ativo=True).count(),
        'policiais_inativos': Policial.objects.filter(ativo=False).count(),
    }
    
    # Distribuição por patente
    policiais_patente = Policial.objects.filter(ativo=True).values('patente').annotate(
        total=Count('id')
    ).order_by('patente')
    
    context['policiais_patente_labels'] = [item['patente'] for item in policiais_patente]
    context['policiais_patente_data'] = [item['total'] for item in policiais_patente]
    
    # Policiais com mais cautelas
    context['top_policiais_cautelas'] = Policial.objects.filter(
        ativo=True
    ).annotate(
        total_cautelas=Count('cautelas')
    ).filter(
        total_cautelas__gt=0
    ).order_by('-total_cautelas')[:10]
    
    # Últimos policiais cadastrados
    context['ultimos_policiais'] = Policial.objects.order_by('-criado_em')[:15]
    
    return render(request, 'dashboard/dashboard_policiais.html', context)


@login_required
def dashboard_cautelas(request):
    """Dashboard de cautelas e devoluções"""
    
    from datetime import timedelta
    
    hoje = timezone.now()
    ultimos_30_dias = hoje - timedelta(days=30)
    
    context = {
        'cautelas_ativas': Cautela.objects.filter(status='ATIVA').count(),
        'cautelas_devolvidas': Cautela.objects.filter(status='DEVOLVIDA').count(),
        'cautelas_parciais': Cautela.objects.filter(status='PARCIAL').count(),
        'cautelas_canceladas': Cautela.objects.filter(status='CANCELADA').count(),
        'total_cautelas': Cautela.objects.count(),
    }
    
    # Cautelas por tipo de item
    itens_por_tipo = ItemCautela.objects.values('tipo_item').annotate(
        total=Count('id')
    )
    
    context['itens_tipo_labels'] = [item['tipo_item'] for item in itens_por_tipo]
    context['itens_tipo_data'] = [item['total'] for item in itens_por_tipo]
    
    # Cautelas por mês (últimos 6 meses)
    ultimos_6_meses = []
    cautelas_por_mes = []
    
    for i in range(5, -1, -1):
        mes = hoje - timedelta(days=30*i)
        mes_inicio = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mes_fim = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)
        
        total = Cautela.objects.filter(
            data_cautela__gte=mes_inicio,
            data_cautela__lte=mes_fim
        ).count()
        
        ultimos_6_meses.append(mes_inicio.strftime('%B/%Y'))
        cautelas_por_mes.append(total)
    
    context['cautelas_meses_labels'] = ultimos_6_meses
    context['cautelas_meses_data'] = cautelas_por_mes
    
    # Últimas cautelas detalhadas
    context['ultimas_cautelas'] = Cautela.objects.select_related(
        'policial', 'criado_por'
    ).prefetch_related('itens').order_by('-data_cautela')[:20]
    
    # Cautelas vencidas (prevista devolução < hoje)
    context['cautelas_vencidas'] = Cautela.objects.filter(
        status='ATIVA',
        data_prevista_devolucao__lt=hoje
    ).select_related('policial').count()
    
    return render(request, 'dashboard/dashboard_cautelas.html', context)


@login_required
def dashboard_viaturas(request):
    """Dashboard de viaturas"""
    
    context = {
        'total_viaturas': Viatura.objects.filter(ativo=True).count(),
        'viaturas_disponiveis': Viatura.objects.filter(status='DISPONIVEL').count(),
        'viaturas_em_uso': Viatura.objects.filter(status='EM_USO').count(),
        'viaturas_manutencao': Viatura.objects.filter(status='MANUTENCAO').count(),
        'viaturas_baixadas': Viatura.objects.filter(status='BAIXADA').count(),
    }
    
    # Viaturas por tipo
    viaturas_tipo = Viatura.objects.filter(ativo=True).values('tipo').annotate(
        total=Count('id')
    )
    
    context['viaturas_tipo_labels'] = [item['tipo'] for item in viaturas_tipo]
    context['viaturas_tipo_data'] = [item['total'] for item in viaturas_tipo]
    
    # Viaturas por marca
    viaturas_marca = Viatura.objects.filter(ativo=True).values('marca').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    context['viaturas_marca_labels'] = [item['marca'] for item in viaturas_marca]
    context['viaturas_marca_data'] = [item['total'] for item in viaturas_marca]
    
    # Últimas viaturas cadastradas
    context['ultimas_viaturas'] = Viatura.objects.filter(
        ativo=True
    ).order_by('-criado_em')[:15]
    
    return render(request, 'dashboard/dashboard_viaturas.html', context)


@login_required
def dashboard_municoes(request):
    """Dashboard de munições"""
    
    context = {
        'total_municoes': Municao.objects.count(),
        'total_estoque': Municao.objects.aggregate(total=Sum('quantidade'))['total'] or 0,
        'estoque_baixo': Municao.objects.filter(quantidade__lte=F('quantidade_minima')).count(),
    }
    
    # Munições com estoque crítico
    context['municoes_criticas'] = Municao.objects.filter(
        quantidade__lte=F('quantidade_minima')
    ).order_by('quantidade')[:15]
    
    # Munições por calibre
    municoes_calibre = Municao.objects.values('calibre').annotate(
        total_quantidade=Sum('quantidade'),
        total_itens=Count('id')
    ).order_by('calibre')
    
    context['municoes_calibre_labels'] = [item['calibre'] for item in municoes_calibre]
    context['municoes_calibre_data'] = [item['total_quantidade'] for item in municoes_calibre]
    
    # Movimentações recentes
    context['movimentacoes_recentes'] = MovimentacaoMunicao.objects.select_related(
        'municao', 'criado_por'
    ).order_by('-data_movimentacao')[:20]
    
    # Munições que vencem em 30 dias
    hoje = timezone.now().date()
    data_vencimento = hoje + timedelta(days=30)
    
    context['municoes_vencendo'] = Municao.objects.filter(
        validade__lte=data_vencimento,
        validade__gte=hoje
    ).order_by('validade')[:10]
    
    return render(request, 'dashboard/dashboard_municoes.html', context)


@login_required
def dashboard_estoque(request):
    """Dashboard de estoque geral"""
    
    context = {
        'equipamentos': Equipamento.objects.filter(ativo=True).count(),
        'eletronicos': Eletronico.objects.filter(ativo=True).count(),
        'mobilias': Mobilia.objects.filter(ativo=True).count(),
    }
    
    # Equipamentos com estoque baixo
    context['equipamentos_baixo'] = Equipamento.objects.filter(
        ativo=True,
        quantidade__lte=F('quantidade_minima')
    ).order_by('quantidade')[:15]
    
    # Equipamentos por categoria
    equipamentos_categoria = Equipamento.objects.filter(ativo=True).values('categoria').annotate(
        total=Count('id'),
        total_quantidade=Sum('quantidade')
    )
    
    context['equipamentos_categoria_labels'] = [item['categoria'] for item in equipamentos_categoria]
    context['equipamentos_categoria_data'] = [item['total'] for item in equipamentos_categoria]
    
    # Eletrônicos por status
    eletronicos_status = Eletronico.objects.filter(ativo=True).values('status').annotate(
        total=Count('id')
    )
    
    context['eletronicos_status_labels'] = [item['status'] for item in eletronicos_status]
    context['eletronicos_status_data'] = [item['total'] for item in eletronicos_status]
    
    # Últimas aquisições (últimos 30 dias)
    ultimos_30_dias = timezone.now() - timedelta(days=30)
    
    context['ultimos_equipamentos'] = Equipamento.objects.filter(
        criado_em__gte=ultimos_30_dias
    ).order_by('-criado_em')[:10]
    
    context['ultimos_eletronicos'] = Eletronico.objects.filter(
        criado_em__gte=ultimos_30_dias
    ).order_by('-criado_em')[:10]
    
    return render(request, 'dashboard/dashboard_estoque.html', context)


@login_required
def dashboard_relatorios(request):
    """Dashboard de relatórios analíticos"""
    
    hoje = timezone.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    context = {
        'total_relatorios': RelatorioAnalitico.objects.filter(status='finalizado').count(),
        'relatorios_mes': RelatorioAnalitico.objects.filter(
            data_ocorrencia__month=mes_atual,
            data_ocorrencia__year=ano_atual,
            status='finalizado'
        ).count(),
        'relatorios_rascunho': RelatorioAnalitico.objects.filter(status='rascunho').count(),
        'relatorios_arquivados': RelatorioAnalitico.objects.filter(status='arquivado').count(),
    }
    
    # Relatórios por mês (últimos 12 meses)
    relatorios_por_mes = []
    meses_labels = []
    
    for i in range(11, -1, -1):
        data = hoje - timedelta(days=30*i)
        total = RelatorioAnalitico.objects.filter(
            data_ocorrencia__year=data.year,
            data_ocorrencia__month=data.month,
            status='finalizado'
        ).count()
        
        meses_labels.append(data.strftime('%B/%Y'))
        relatorios_por_mes.append(total)
    
    context['relatorios_meses_labels'] = meses_labels
    context['relatorios_meses_data'] = relatorios_por_mes
    
    # Últimos relatórios
    context['ultimos_relatorios'] = RelatorioAnalitico.objects.filter(
        status='finalizado'
    ).select_related().order_by('-data_ocorrencia')[:20]
    
    # Localidades com mais ocorrências
    locais = RelatorioAnalitico.objects.filter(
        status='finalizado'
    ).values('local').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    context['locais_top_labels'] = [item['local'][:30] for item in locais]
    context['locais_top_data'] = [item['total'] for item in locais]
    
    return render(request, 'dashboard/dashboard_relatorios.html', context)


@login_required
def dashboard_escalas(request):
    """Dashboard de escalas diárias"""
    
    context = {
        'total_escalas': EscalaGerada.objects.count(),
        'escalas_mes': EscalaGerada.objects.filter(
            data_escala__month=timezone.now().month
        ).count(),
    }
    
    # Escalas por mês
    escalas_por_mes = []
    meses_labels = []
    
    for i in range(5, -1, -1):
        data = timezone.now() - timedelta(days=30*i)
        total = EscalaGerada.objects.filter(
            data_escala__year=data.year,
            data_escala__month=data.month
        ).count()
        
        meses_labels.append(data.strftime('%B/%Y'))
        escalas_por_mes.append(total)
    
    context['escalas_meses_labels'] = meses_labels
    context['escalas_meses_data'] = escalas_por_mes
    
    # Últimas escalas
    context['ultimas_escalas'] = EscalaGerada.objects.select_related(
        'criado_por'
    ).order_by('-data_escala')[:15]
    
    return render(request, 'dashboard/dashboard_escalas.html', context)


@login_required
def dashboard_apreendidos(request):
    """Dashboard de veículos apreendidos"""
    
    context = {
        'total_apreendidos': VeiculoApreendido.objects.count(),
        'nao_devolvidos': VeiculoApreendido.objects.filter(devolvido=False).count(),
        'devolvidos': VeiculoApreendido.objects.filter(devolvido=True).count(),
    }
    
    # Apreensões por mês
    apreensoes_por_mes = []
    meses_labels = []
    
    for i in range(5, -1, -1):
        data = timezone.now() - timedelta(days=30*i)
        total = VeiculoApreendido.objects.filter(
            data_apreensao__year=data.year,
            data_apreensao__month=data.month
        ).count()
        
        meses_labels.append(data.strftime('%B/%Y'))
        apreensoes_por_mes.append(total)
    
    context['apreensoes_meses_labels'] = meses_labels
    context['apreensoes_meses_data'] = apreensoes_por_mes
    
    # Modelos mais apreendidos
    modelos = VeiculoApreendido.objects.values('modelo').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    context['modelos_top_labels'] = [item['modelo'] for item in modelos]
    context['modelos_top_data'] = [item['total'] for item in modelos]
    
    # Últimos apreendidos
    context['ultimos_apreendidos'] = VeiculoApreendido.objects.filter(
        devolvido=False
    ).order_by('-data_apreensao')[:20]
    
    return render(request, 'dashboard/dashboard_apreendidos.html', context)


@login_required
def api_chart_data(request, chart_type):
    """API para dados de gráficos (AJAX)"""
    from django.http import JsonResponse
    
    data = {}
    
    if chart_type == 'policiais_patente':
        dados = Policial.objects.filter(ativo=True).values('patente').annotate(
            total=Count('id')
        )
        data = {
            'labels': [item['patente'] for item in dados],
            'values': [item['total'] for item in dados]
        }
    
    elif chart_type == 'armamentos_status':
        dados = Armamento.objects.filter(ativo=True).values('status').annotate(
            total=Count('id')
        )
        data = {
            'labels': [item['status'] for item in dados],
            'values': [item['total'] for item in dados]
        }
    
    elif chart_type == 'cautelas_mensais':
        hoje = timezone.now()
        labels = []
        values = []
        
        for i in range(5, -1, -1):
            mes = hoje - timedelta(days=30*i)
            mes_inicio = mes.replace(day=1, hour=0, minute=0)
            mes_fim = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)
            
            total = Cautela.objects.filter(
                data_cautela__gte=mes_inicio,
                data_cautela__lte=mes_fim
            ).count()
            
            labels.append(mes_inicio.strftime('%B/%Y'))
            values.append(total)
        
        data = {'labels': labels, 'values': values}
    
    return JsonResponse(data)