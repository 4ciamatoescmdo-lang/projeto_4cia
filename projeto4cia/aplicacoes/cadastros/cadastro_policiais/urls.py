from django.urls import path
from . import views

app_name = 'cadastro_policiais'

urlpatterns = [
    # URLs principais do Policial
    path('', views.PolicialListView.as_view(), name='policial_list'),
    path('novo/', views.PolicialCreateView.as_view(), name='policial_create'),
    path('<int:pk>/', views.PolicialDetailView.as_view(), name='policial_detail'),
    path('<int:pk>/editar/', views.PolicialUpdateView.as_view(), name='policial_update'),
    path('<int:pk>/excluir/', views.PolicialDeleteView.as_view(), name='policial_delete'),
    path('assinatura/<int:policial_id>/', views.get_assinatura, name='get_assinatura'),
]