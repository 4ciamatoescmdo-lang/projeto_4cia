from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Comandante

class ComandanteListView(ListView):
    model = Comandante
    template_name = 'cadastro_comandante/comandante_list.html'
    context_object_name = 'comandantes'
    ordering = ['-data_nomeacao']