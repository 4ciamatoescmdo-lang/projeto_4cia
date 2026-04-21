from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'cadastro_eletronicos'

urlpatterns = [
    path('', login_required(views.EletronicoListView.as_view()), name='eletronico_list'),
    path('novo/', login_required(views.EletronicoCreateView.as_view()), name='eletronico_create'),
    path('<int:pk>/', login_required(views.EletronicoDetailView.as_view()), name='eletronico_detail'),
    path('<int:pk>/editar/', login_required(views.EletronicoUpdateView.as_view()), name='eletronico_update'),
    path('<int:pk>/excluir/', login_required(views.EletronicoDeleteView.as_view()), name='eletronico_delete'),
]