from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'cadastro_armamentos'

urlpatterns = [
    path('', login_required(views.ArmamentoListView.as_view()), name='armamento_list'),
    path('novo/', login_required(views.ArmamentoCreateView.as_view()), name='armamento_create'),
    path('<int:pk>/', login_required(views.ArmamentoDetailView.as_view()), name='armamento_detail'),
    path('<int:pk>/editar/', login_required(views.ArmamentoUpdateView.as_view()), name='armamento_update'),
    path('<int:pk>/excluir/', login_required(views.ArmamentoDeleteView.as_view()), name='armamento_delete'),
]