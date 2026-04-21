from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Mobilia
from .forms import MobiliaForm

class MobiliaListView(LoginRequiredMixin, ListView):
    model = Mobilia
    template_name = 'cadastro_mobilia/mobilia_list.html'
    context_object_name = 'mobilia'
    paginate_by = 20

class MobiliaDetailView(LoginRequiredMixin, DetailView):
    model = Mobilia
    template_name = 'cadastro_mobilia/mobilia_detail.html'
    context_object_name = 'mobilia'

class MobiliaCreateView(LoginRequiredMixin, CreateView):
    model = Mobilia
    form_class = MobiliaForm
    template_name = 'cadastro_mobilia/mobilia_form.html'
    success_url = reverse_lazy('cadastro_mobilia:mobilia_list')

class MobiliaUpdateView(LoginRequiredMixin, UpdateView):
    model = Mobilia
    form_class = MobiliaForm
    template_name = 'cadastro_mobilia/mobilia_form.html'
    success_url = reverse_lazy('cadastro_mobilia:mobilia_list')

class MobiliaDeleteView(LoginRequiredMixin, DeleteView):
    model = Mobilia
    template_name = 'cadastro_mobilia/mobilia_confirm_delete.html'
    success_url = reverse_lazy('cadastro_mobilia:mobilia_list')