from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from .models import RelatorioAnalitico, PessoaEnvolvida, NumeroRelatorio

def form_relatorio(request):
    """View para exibir o formulário de relatório"""
    # Gerar número do relatório diretamente no backend
    from django.utils import timezone
    ano = timezone.now().year
    controle, _ = NumeroRelatorio.objects.get_or_create(ano=ano)
    proximo_numero = controle.ultimo_numero + 1
    numero_formatado = f"{proximo_numero:04d}/{ano}"
    
    context = {
        'relatorio_numero': numero_formatado,
        'proximo_numero': proximo_numero,
        'ano_atual': ano
    }
    return render(request, 'relatorio_analitico/form_relatorio.html', context)

def salvar_relatorio(request):
    """View para salvar o relatório"""
    if request.method == 'POST':
        try:
            # Obter o número do relatório do formulário
            numero_relatorio_str = request.POST.get('numero_relatorio', '')
            
            # Se não veio do formulário, gerar um novo
            if not numero_relatorio_str:
                numero_relatorio = NumeroRelatorio.get_proximo_numero()
            else:
                numero_relatorio = numero_relatorio_str
                # Atualizar o contador
                ano = timezone.now().year
                partes = numero_relatorio.split('/')
                if len(partes) == 2:
                    num = int(partes[0])
                    controle, _ = NumeroRelatorio.objects.get_or_create(ano=ano)
                    if num > controle.ultimo_numero:
                        controle.ultimo_numero = num
                        controle.save()
            
            # Criar o relatório principal
            relatorio = RelatorioAnalitico.objects.create(
                numero_relatorio=numero_relatorio,
                codigo_ocorrencia=request.POST.get('codigo_ocorrencia', ''),
                local=request.POST.get('local', ''),
                data_ocorrencia=request.POST.get('data') or timezone.now().date(),
                hora_ocorrencia=request.POST.get('hora') or timezone.now().time(),
                instrumento_usado=request.POST.get('instrumento', ''),
                materiais_apreendidos=request.POST.get('materiais', ''),
                evadiu_se=bool(request.POST.get('evadiu')),
                samu_acionado=bool(request.POST.get('samu')),
                conduzido_delegacia=bool(request.POST.get('detido')),
                viaturas_guarnicoes=request.POST.get('viaturas', ''),
                relato=request.POST.get('relato', ''),
                providencias=request.POST.get('providencias', ''),
                criado_por=request.user.username if request.user.is_authenticated else 'Sistema'
            )
            
            # Salvar pessoas envolvidas
            nomes = request.POST.getlist('pessoa_nome[]')
            tipos = request.POST.getlist('pessoa_tipo[]')
            cpfs = request.POST.getlist('pessoa_cpf[]')
            rgs = request.POST.getlist('pessoa_rg[]')
            enderecos = request.POST.getlist('pessoa_endereco[]')
            nomes_mae = request.POST.getlist('pessoa_mae[]')
            
            for i in range(len(nomes)):
                if nomes[i]:  # Só salvar se tiver nome
                    PessoaEnvolvida.objects.create(
                        relatorio=relatorio,
                        tipo=tipos[i] if i < len(tipos) else 'acusado',
                        nome=nomes[i],
                        cpf=cpfs[i] if i < len(cpfs) else '',
                        rg=rgs[i] if i < len(rgs) else '',
                        endereco=enderecos[i] if i < len(enderecos) else '',
                        nome_mae=nomes_mae[i] if i < len(nomes_mae) else ''
                    )
            
            messages.success(request, f'Relatório {numero_relatorio} salvo com sucesso!')
            return redirect('relatorio_analitico:visualizar_relatorio', pk=relatorio.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {str(e)}')
            return redirect('relatorio_analitico:form_relatorio')
    
    return redirect('relatorio_analitico:form_relatorio')

def lista_relatorios(request):
    """View para listar todos os relatórios"""
    relatorios = RelatorioAnalitico.objects.all().order_by('-data_ocorrencia')
    context = {'relatorios': relatorios}
    return render(request, 'relatorio_analitico/lista_relatorios.html', context)

def visualizar_relatorio(request, pk):
    """View para visualizar um relatório específico"""
    relatorio = get_object_or_404(RelatorioAnalitico, pk=pk)
    context = {'relatorio': relatorio}
    return render(request, 'relatorio_analitico/visualizar_relatorio.html', context)

def editar_relatorio(request, pk):
    """View para editar um relatório"""
    relatorio = get_object_or_404(RelatorioAnalitico, pk=pk)
    
    if request.method == 'POST':
        try:
            # Atualizar o relatório
            relatorio.codigo_ocorrencia = request.POST.get('codigo_ocorrencia', '')
            relatorio.local = request.POST.get('local', '')
            relatorio.data_ocorrencia = request.POST.get('data') or relatorio.data_ocorrencia
            relatorio.hora_ocorrencia = request.POST.get('hora') or relatorio.hora_ocorrencia
            relatorio.instrumento_usado = request.POST.get('instrumento', '')
            relatorio.materiais_apreendidos = request.POST.get('materiais', '')
            relatorio.evadiu_se = bool(request.POST.get('evadiu'))
            relatorio.samu_acionado = bool(request.POST.get('samu'))
            relatorio.conduzido_delegacia = bool(request.POST.get('detido'))
            relatorio.viaturas_guarnicoes = request.POST.get('viaturas', '')
            relatorio.relato = request.POST.get('relato', '')
            relatorio.providencias = request.POST.get('providencias', '')
            relatorio.save()
            
            # Atualizar pessoas (remover todas e recriar)
            relatorio.pessoas.all().delete()
            
            nomes = request.POST.getlist('pessoa_nome[]')
            tipos = request.POST.getlist('pessoa_tipo[]')
            cpfs = request.POST.getlist('pessoa_cpf[]')
            rgs = request.POST.getlist('pessoa_rg[]')
            enderecos = request.POST.getlist('pessoa_endereco[]')
            nomes_mae = request.POST.getlist('pessoa_mae[]')
            
            for i in range(len(nomes)):
                if nomes[i]:
                    PessoaEnvolvida.objects.create(
                        relatorio=relatorio,
                        tipo=tipos[i] if i < len(tipos) else 'acusado',
                        nome=nomes[i],
                        cpf=cpfs[i] if i < len(cpfs) else '',
                        rg=rgs[i] if i < len(rgs) else '',
                        endereco=enderecos[i] if i < len(enderecos) else '',
                        nome_mae=nomes_mae[i] if i < len(nomes_mae) else ''
                    )
            
            messages.success(request, 'Relatório atualizado com sucesso!')
            return redirect('relatorio_analitico:visualizar_relatorio', pk=relatorio.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {str(e)}')
    
    context = {'relatorio': relatorio}
    return render(request, 'relatorio_analitico/editar_relatorio.html', context)

def excluir_relatorio(request, pk):
    """View para excluir um relatório"""
    relatorio = get_object_or_404(RelatorioAnalitico, pk=pk)
    
    if request.method == 'POST':
        numero = relatorio.numero_relatorio
        relatorio.delete()
        messages.success(request, f'Relatório {numero} excluído com sucesso!')
        return redirect('relatorio_analitico:lista_relatorios')
    
    context = {'relatorio': relatorio}
    return render(request, 'relatorio_analitico/confirmar_exclusao.html', context)

def imprimir_relatorio(request, pk):
    """View para imprimir um relatório salvo"""
    relatorio = get_object_or_404(RelatorioAnalitico, pk=pk)
    
    # Renderizar o template de impressão
    html = render_to_string('relatorio_analitico/impressao_relatorio.html', {'relatorio': relatorio})
    
    # Retornar como HTML para impressão
    return HttpResponse(html)