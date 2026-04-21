from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'cadastro_equipamentos'

urlpatterns = [
    path('', login_required(views.EquipamentoListView.as_view()), name='equipamento_list'),
    path('novo/', login_required(views.EquipamentoCreateView.as_view()), name='equipamento_create'),
    path('<int:pk>/', login_required(views.EquipamentoDetailView.as_view()), name='equipamento_detail'),
    path('<int:pk>/editar/', login_required(views.EquipamentoUpdateView.as_view()), name='equipamento_update'),
    path('<int:pk>/excluir/', login_required(views.EquipamentoDeleteView.as_view()), name='equipamento_delete'),
]