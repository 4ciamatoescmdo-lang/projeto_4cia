# aplicacoes/cadastros/cadastro_veiculo_apreendido/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from .models import VeiculoApreendido, DevolucaoVeiculo
from .forms import VeiculoApreendidoForm, DevolucaoVeiculoForm

# Tente importar xhtml2pdf dinamicamente; se não estiver instalado, marcar como indisponível
import importlib

pisa = None
try:
    # Importa explicitamente o submódulo 'xhtml2pdf.pisa' para obter o objeto 'pisa'
    pisa = importlib.import_module('xhtml2pdf.pisa')
    PDF_AVAILABLE = True
except ImportError:
    pisa = None
    PDF_AVAILABLE = False

@login_required
def lista_veiculos(request):
    veiculos = VeiculoApreendido.objects.all().order_by('-data_apreensao')
    context = {
        'veiculos': veiculos,
        'titulo': 'Veículos Apreendidos'
    }
    return render(request, 'cadastro_veiculo_apreendido/lista_veiculos.html', context)

@login_required
def novo_veiculo(request):
    if request.method == 'POST':
        form = VeiculoApreendidoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo apreendido cadastrado com sucesso!')
            return redirect('cadastro_veiculo_apreendido:lista')
    else:
        form = VeiculoApreendidoForm()
    
    context = {
        'form': form,
        'titulo': 'Novo Veículo Apreendido'
    }
    return render(request, 'cadastro_veiculo_apreendido/form_veiculo.html', context)

@login_required
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(VeiculoApreendido, pk=pk)
    
    if request.method == 'POST':
        form = VeiculoApreendidoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo atualizado com sucesso!')
            return redirect('cadastro_veiculo_apreendido:lista')
    else:
        form = VeiculoApreendidoForm(instance=veiculo)
    
    context = {
        'form': form,
        'veiculo': veiculo,
        'titulo': 'Editar Veículo Apreendido'
    }
    return render(request, 'cadastro_veiculo_apreendido/form_veiculo.html', context)

@login_required
def excluir_veiculo(request, pk):
    veiculo = get_object_or_404(VeiculoApreendido, pk=pk)
    
    if request.method == 'POST':
        veiculo.delete()
        messages.success(request, 'Veículo excluído com sucesso!')
        return redirect('cadastro_veiculo_apreendido:lista')
    
    context = {
        'veiculo': veiculo,
        'titulo': 'Excluir Veículo Apreendido'
    }
    return render(request, 'cadastro_veiculo_apreendido/confirmar_exclusao.html', context)

@login_required
def devolver_veiculo(request, pk):
    veiculo = get_object_or_404(VeiculoApreendido, pk=pk)
    
    # Verificar se o veículo já foi devolvido
    if veiculo.devolvido:
        messages.warning(request, 'Este veículo já foi devolvido!')
        return redirect('cadastro_veiculo_apreendido:lista')
    
    if request.method == 'POST':
        form = DevolucaoVeiculoForm(request.POST)
        if form.is_valid():
            devolucao = form.save(commit=False)
            devolucao.veiculo = veiculo
            devolucao.responsavel_devolucao = request.user
            devolucao.save()
            
            # Atualizar o veículo como devolvido
            veiculo.devolvido = True
            veiculo.data_devolucao = timezone.now().date()
            veiculo.save()
            
            messages.success(request, 'Devolução registrada com sucesso!')
            return redirect('cadastro_veiculo_apreendido:imprimir_devolucao', pk=devolucao.pk)
    else:
        form = DevolucaoVeiculoForm()
    
    context = {
        'form': form,
        'veiculo': veiculo,
        'titulo': f'Devolução do Veículo: {veiculo.modelo} - {veiculo.placa}'
    }
    return render(request, 'cadastro_veiculo_apreendido/devolucao_veiculo.html', context)

@login_required
def imprimir_devolucao(request, pk):
    devolucao = get_object_or_404(DevolucaoVeiculo, pk=pk)
    
    if not PDF_AVAILABLE:
        # Se xhtml2pdf não estiver instalado, mostra a versão HTML
        context = {'devolucao': devolucao}
        return render(request, 'cadastro_veiculo_apreendido/termo_devolucao_html.html', context)
    
    # Template para o PDF
    template_path = 'cadastro_veiculo_apreendido/termo_devolucao_pdf.html'
    context = {'devolucao': devolucao}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="termo_devolucao_{devolucao.veiculo.placa}_{devolucao.data_devolucao}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    # Gerar PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)
    
    return response