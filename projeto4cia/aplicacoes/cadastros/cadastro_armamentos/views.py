from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Armamento
from .forms import ArmamentoForm

class ArmamentoListView(LoginRequiredMixin, ListView):
    model = Armamento
    template_name = 'cadastro_armamentos/armamento_list.html'
    context_object_name = 'armamentos'
    paginate_by = 20

class ArmamentoDetailView(LoginRequiredMixin, DetailView):
    model = Armamento
    template_name = 'cadastro_armamentos/armamento_detail.html'
    context_object_name = 'armamento'

class ArmamentoCreateView(LoginRequiredMixin, CreateView):
    model = Armamento
    form_class = ArmamentoForm
    template_name = 'cadastro_armamentos/armamento_form.html'
    success_url = reverse_lazy('cadastro_armamentos:armamento_list')

class ArmamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Armamento
    form_class = ArmamentoForm
    template_name = 'cadastro_armamentos/armamento_form.html'
    success_url = reverse_lazy('cadastro_armamentos:armamento_list')

class ArmamentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Armamento
    template_name = 'cadastro_armamentos/armamento_confirm_delete.html'
    success_url = reverse_lazy('cadastro_armamentos:armamento_list')