from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Viatura
from .forms import ViaturaForm

class ViaturaListView(LoginRequiredMixin, ListView):
    model = Viatura
    template_name = 'cadastro_vtrs/vtr_list.html'
    context_object_name = 'viaturas'
    paginate_by = 20
    login_url = 'login'

class ViaturaDetailView(LoginRequiredMixin, DetailView):
    model = Viatura
    template_name = 'cadastro_vtrs/vtr_detail.html'
    context_object_name = 'viatura'
    login_url = 'login'

class ViaturaCreateView(LoginRequiredMixin, CreateView):
    model = Viatura
    form_class = ViaturaForm
    template_name = 'cadastro_vtrs/vtr_form.html'
    success_url = reverse_lazy('cadastro_vtrs:vtr_list')
    login_url = 'login'

class ViaturaUpdateView(LoginRequiredMixin, UpdateView):
    model = Viatura
    form_class = ViaturaForm
    template_name = 'cadastro_vtrs/vtr_form.html'
    success_url = reverse_lazy('cadastro_vtrs:vtr_list')
    login_url = 'login'

class ViaturaDeleteView(LoginRequiredMixin, DeleteView):
    model = Viatura
    template_name = 'cadastro_vtrs/vtr_confirm_delete.html'
    success_url = reverse_lazy('cadastro_vtrs:vtr_list')
    login_url = 'login'