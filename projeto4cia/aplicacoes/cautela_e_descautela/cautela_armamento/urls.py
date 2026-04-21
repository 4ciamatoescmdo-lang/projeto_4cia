from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'cautela_armamento'

urlpatterns = [
    path('', login_required(views.CautelaListView.as_view()), name='cautela_list'),
    path('nova/', login_required(views.CautelaCreateView.as_view()), name='cautela_create'),
    path('<int:pk>/', login_required(views.CautelaDetailView.as_view()), name='cautela_detail'),
    path('<int:pk>/editar/', login_required(views.CautelaUpdateView.as_view()), name='cautela_update'),
    path('<int:pk>/excluir/', login_required(views.CautelaDeleteView.as_view()), name='cautela_delete'),
    path('<int:pk>/devolver/', login_required(views.RegistrarDevolucaoView.as_view()), name='cautela_devolucao'),
]