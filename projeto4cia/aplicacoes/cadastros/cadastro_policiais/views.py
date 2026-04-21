from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Policial
from .forms import PolicialForm

class PolicialListView(ListView):
    model = Policial
    template_name = 'cadastro_policiais/policial_list.html'
    context_object_name = 'policiais'
    paginate_by = 20

class PolicialDetailView(DetailView):
    model = Policial
    template_name = 'cadastro_policiais/policial_detail.html'
    context_object_name = 'policial'

class PolicialCreateView(CreateView):
    model = Policial
    form_class = PolicialForm
    template_name = 'cadastro_policiais/policial_form.html'
    success_url = reverse_lazy('cadastro_policiais:policial_list')

class PolicialUpdateView(UpdateView):
    model = Policial
    form_class = PolicialForm
    template_name = 'cadastro_policiais/policial_form.html'
    success_url = reverse_lazy('cadastro_policiais:policial_list')

class PolicialDeleteView(DeleteView):
    model = Policial
    template_name = 'cadastro_policiais/policial_confirm_delete.html'
    success_url = reverse_lazy('cadastro_policiais:policial_list')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import os

def get_assinatura(request, policial_id):
    """Retorna a assinatura do policial em base64"""
    try:
        from .models import Policial
        policial = Policial.objects.get(id=policial_id)
        
        if policial.assinatura and policial.assinatura.url:
            # Ler o arquivo da assinatura e converter para base64
            with open(policial.assinatura.path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                # Detectar o formato da imagem
                ext = policial.assinatura.name.split('.')[-1].lower()
                mime_type = f'image/{ext}'
                if ext == 'jpg':
                    mime_type = 'image/jpeg'
                img_base64 = f'data:{mime_type};base64,{img_data}'
                
                return JsonResponse({
                    'success': True,
                    'assinatura': img_base64
                })
        
        return JsonResponse({
            'success': False,
            'message': 'Policial não possui assinatura cadastrada'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })