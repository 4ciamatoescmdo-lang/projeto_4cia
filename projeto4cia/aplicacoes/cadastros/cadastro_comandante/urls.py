from django.urls import path
from . import views

app_name = 'cadastro_comandante'

urlpatterns = [
    path('', views.ComandanteListView.as_view(), name='comandante_list'),
    # ... outras URLs existentes
]