from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'cadastro_municoes'

urlpatterns = [
    path('', login_required(views.MunicaoListView.as_view()), name='municao_list'),
    path('nova/', login_required(views.MunicaoCreateView.as_view()), name='municao_create'),
    path('<int:pk>/editar/', login_required(views.MunicaoUpdateView.as_view()), name='municao_update'),
]