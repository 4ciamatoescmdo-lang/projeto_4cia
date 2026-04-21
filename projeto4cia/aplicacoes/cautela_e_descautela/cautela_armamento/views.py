from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Cautela, ItemCautela
from .forms import CautelaForm
from aplicacoes.cadastros.cadastro_municoes.models import Municao, MovimentacaoMunicao  # <-- IMPORTAR

class CautelaListView(LoginRequiredMixin, ListView):
    model = Cautela
    template_name = 'cautela_armamento/cautela_list.html'
    context_object_name = 'cautelas'
    paginate_by = 20
    ordering = ['-data_cautela']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtrar por armeiro que CAUTELOU (criado_por)
        armeiro = self.request.GET.get('armeiro')
        if armeiro:
            queryset = queryset.filter(criado_por_id=armeiro)
        
        # Filtrar por armeiro que DEVOLVEU (devolvido_por)
        devolvido_por = self.request.GET.get('devolvido_por')
        if devolvido_por:
            queryset = queryset.filter(devolvido_por_id=devolvido_por)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar lista de usuários para os filtros
        context['users'] = User.objects.filter(is_active=True).order_by('username')
        return context

class CautelaDetailView(LoginRequiredMixin, DetailView):
    model = Cautela
    template_name = 'cautela_armamento/cautela_detail.html'
    context_object_name = 'cautela'

class CautelaCreateView(LoginRequiredMixin, CreateView):
    model = Cautela
    form_class = CautelaForm
    template_name = 'cautela_armamento/cautela_form.html'
    success_url = reverse_lazy('cautela_armamento:cautela_list')

    def form_valid(self, form):
        # Salvar a cautela primeiro
        self.object = form.save(commit=False)
        self.object.criado_por = self.request.user
        self.object.save()
        
        # Processar armamento principal
        if form.cleaned_data.get('armamento_principal'):
            ItemCautela.objects.create(
                cautela=self.object,
                tipo_item='ARMAMENTO_PRINCIPAL',
                armamento=form.cleaned_data['armamento_principal']
            )
            armamento = form.cleaned_data['armamento_principal']
            armamento.status = 'EM_USO'
            armamento.save()
        
        # Processar armamento secundário
        if form.cleaned_data.get('armamento_secundario'):
            ItemCautela.objects.create(
                cautela=self.object,
                tipo_item='ARMAMENTO_SECUNDARIO',
                armamento=form.cleaned_data['armamento_secundario']
            )
            armamento = form.cleaned_data['armamento_secundario']
            armamento.status = 'EM_USO'
            armamento.save()
        
        # Processar equipamentos
        for i in range(1, 5):
            equipamento = form.cleaned_data.get(f'equipamento_0{i}')
            if equipamento:
                ItemCautela.objects.create(
                    cautela=self.object,
                    tipo_item='EQUIPAMENTO',
                    equipamento=equipamento
                )
                equipamento.status = 'EM_USO'
                equipamento.save()
        
        # ===== PROCESSAR MUNIÇÃO 01 COM SUBTRAÇÃO DE ESTOQUE =====
        municao_01 = form.cleaned_data.get('tipo_municao_01')
        quantidade_01 = form.cleaned_data.get('quantidade_municao_01')
        
        if municao_01 and quantidade_01:
            # Criar o item da cautela
            ItemCautela.objects.create(
                cautela=self.object,
                tipo_item='MUNICAO',
                municao=municao_01,
                quantidade_municao=quantidade_01
            )
            
            # DAR BAIXA NO ESTOQUE
            municao_01.dar_baixa(quantidade_01)
            
            # Registrar a movimentação
            MovimentacaoMunicao.objects.create(
                municao=municao_01,
                tipo='SAIDA_CAUTELA',
                quantidade=quantidade_01,
                cautela=self.object,
                observacao=f"Cautela #{self.object.id}",
                criado_por=self.request.user
            )
        
        # ===== PROCESSAR MUNIÇÃO 02 COM SUBTRAÇÃO DE ESTOQUE =====
        municao_02 = form.cleaned_data.get('tipo_municao_02')
        quantidade_02 = form.cleaned_data.get('quantidade_municao_02')
        
        if municao_02 and quantidade_02:
            ItemCautela.objects.create(
                cautela=self.object,
                tipo_item='MUNICAO',
                municao=municao_02,
                quantidade_municao=quantidade_02
            )
            
            # DAR BAIXA NO ESTOQUE
            municao_02.dar_baixa(quantidade_02)
            
            # Registrar a movimentação
            MovimentacaoMunicao.objects.create(
                municao=municao_02,
                tipo='SAIDA_CAUTELA',
                quantidade=quantidade_02,
                cautela=self.object,
                observacao=f"Cautela #{self.object.id}",
                criado_por=self.request.user
            )
        
        messages.success(self.request, 'Cautela registrada com sucesso!')
        return super().form_valid(form)

class CautelaUpdateView(LoginRequiredMixin, UpdateView):
    model = Cautela
    form_class = CautelaForm
    template_name = 'cautela_armamento/cautela_form.html'
    success_url = reverse_lazy('cautela_armamento:cautela_list')

class CautelaDeleteView(LoginRequiredMixin, DeleteView):
    model = Cautela
    template_name = 'cautela_armamento/cautela_confirm_delete.html'
    success_url = reverse_lazy('cautela_armamento:cautela_list')

class RegistrarDevolucaoView(LoginRequiredMixin, UpdateView):
    model = Cautela
    fields = ['observacoes']
    template_name = 'cautela_armamento/cautela_devolucao.html'
    success_url = reverse_lazy('cautela_armamento:cautela_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = 'DEVOLVIDA'
        self.object.data_devolucao = timezone.now()
        self.object.devolvido_por = self.request.user
        self.object.save()
        
        # Atualizar status dos itens e devolver munição ao estoque
        for item in self.object.itens.all():
            item.devolvido = True
            item.data_devolucao_item = timezone.now()
            item.save()
            
            if item.armamento:
                item.armamento.status = 'DISPONIVEL'
                item.armamento.save()
            
            if item.equipamento:
                item.equipamento.status = 'DISPONIVEL'
                item.equipamento.save()
            
            # ===== DEVOLVER MUNIÇÃO AO ESTOQUE =====
            if item.municao and item.quantidade_municao:
                # Repor estoque
                item.municao.repor_estoque(item.quantidade_municao)
                
                # Registrar movimentação de devolução
                MovimentacaoMunicao.objects.create(
                    municao=item.municao,
                    tipo='DEVOLUCAO_CAUTELA',
                    quantidade=item.quantidade_municao,
                    cautela=self.object,
                    observacao=f"Devolução da cautela #{self.object.id}",
                    criado_por=self.request.user
                )
        
        messages.success(self.request, 'Devolução registrada com sucesso!')
        return super().form_valid(form)