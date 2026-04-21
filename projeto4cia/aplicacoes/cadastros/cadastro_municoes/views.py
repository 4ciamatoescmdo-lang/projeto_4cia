from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from .models import Municao
from .forms import MunicaoForm

class MunicaoListView(LoginRequiredMixin, ListView):
    model = Municao
    template_name = 'cadastro_municoes/municao_list.html'
    context_object_name = 'municoes'
    paginate_by = 20
    ordering = ['calibre', 'fabricante']

class MunicaoCreateView(LoginRequiredMixin, CreateView):
    model = Municao
    form_class = MunicaoForm
    template_name = 'cadastro_municoes/municao_form.html'
    success_url = reverse_lazy('cadastro_municoes:municao_list')

class MunicaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Municao
    form_class = MunicaoForm
    template_name = 'cadastro_municoes/municao_form.html'
    success_url = reverse_lazy('cadastro_municoes:municao_list')