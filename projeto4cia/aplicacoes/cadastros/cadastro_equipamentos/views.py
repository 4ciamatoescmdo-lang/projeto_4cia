from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Equipamento
from .forms import EquipamentoForm

class EquipamentoListView(LoginRequiredMixin, ListView):
    model = Equipamento
    template_name = 'cadastro_equipamentos/equipamento_list.html'
    context_object_name = 'equipamentos'
    paginate_by = 20

class EquipamentoDetailView(LoginRequiredMixin, DetailView):
    model = Equipamento
    template_name = 'cadastro_equipamentos/equipamento_detail.html'
    context_object_name = 'equipamento'

class EquipamentoCreateView(LoginRequiredMixin, CreateView):
    model = Equipamento
    form_class = EquipamentoForm
    template_name = 'cadastro_equipamentos/equipamento_form.html'
    success_url = reverse_lazy('cadastro_equipamentos:equipamento_list')

class EquipamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipamento
    form_class = EquipamentoForm
    template_name = 'cadastro_equipamentos/equipamento_form.html'
    success_url = reverse_lazy('cadastro_equipamentos:equipamento_list')

class EquipamentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipamento
    template_name = 'cadastro_equipamentos/equipamento_confirm_delete.html'
    success_url = reverse_lazy('cadastro_equipamentos:equipamento_list')