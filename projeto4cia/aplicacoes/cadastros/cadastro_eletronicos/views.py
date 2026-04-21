from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Eletronico
from .forms import EletronicoForm

class EletronicoListView(LoginRequiredMixin, ListView):
    model = Eletronico
    template_name = 'cadastro_eletronicos/eletronico_list.html'
    context_object_name = 'eletronicos'
    paginate_by = 20

class EletronicoDetailView(LoginRequiredMixin, DetailView):
    model = Eletronico
    template_name = 'cadastro_eletronicos/eletronico_detail.html'
    context_object_name = 'eletronico'

class EletronicoCreateView(LoginRequiredMixin, CreateView):
    model = Eletronico
    form_class = EletronicoForm
    template_name = 'cadastro_eletronicos/eletronico_form.html'
    success_url = reverse_lazy('cadastro_eletronicos:eletronico_list')

class EletronicoUpdateView(LoginRequiredMixin, UpdateView):
    model = Eletronico
    form_class = EletronicoForm
    template_name = 'cadastro_eletronicos/eletronico_form.html'
    success_url = reverse_lazy('cadastro_eletronicos:eletronico_list')

class EletronicoDeleteView(LoginRequiredMixin, DeleteView):
    model = Eletronico
    template_name = 'cadastro_eletronicos/eletronico_confirm_delete.html'
    success_url = reverse_lazy('cadastro_eletronicos:eletronico_list')