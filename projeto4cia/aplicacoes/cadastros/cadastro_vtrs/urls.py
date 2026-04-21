from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'cadastro_vtrs'

urlpatterns = [
    path('', login_required(views.ViaturaListView.as_view()), name='vtr_list'),
    path('novo/', login_required(views.ViaturaCreateView.as_view()), name='vtr_create'),
    path('<int:pk>/', login_required(views.ViaturaDetailView.as_view()), name='vtr_detail'),
    path('<int:pk>/editar/', login_required(views.ViaturaUpdateView.as_view()), name='vtr_update'),
    path('<int:pk>/excluir/', login_required(views.ViaturaDeleteView.as_view()), name='vtr_delete'),
]