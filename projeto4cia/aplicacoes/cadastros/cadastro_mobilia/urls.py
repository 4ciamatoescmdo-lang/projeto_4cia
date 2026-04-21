from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'cadastro_mobilia'

urlpatterns = [
    path('', login_required(views.MobiliaListView.as_view()), name='mobilia_list'),
    path('novo/', login_required(views.MobiliaCreateView.as_view()), name='mobilia_create'),
    path('<int:pk>/', login_required(views.MobiliaDetailView.as_view()), name='mobilia_detail'),
    path('<int:pk>/editar/', login_required(views.MobiliaUpdateView.as_view()), name='mobilia_update'),
    path('<int:pk>/excluir/', login_required(views.MobiliaDeleteView.as_view()), name='mobilia_delete'),
]