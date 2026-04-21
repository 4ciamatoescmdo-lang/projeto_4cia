# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboards principais
    path('', views.dashboard_home, name='home'),
    path('armamentos/', views.dashboard_armamentos, name='armamentos'),
    path('policiais/', views.dashboard_policiais, name='policiais'),
    path('cautelas/', views.dashboard_cautelas, name='cautelas'),
    path('viaturas/', views.dashboard_viaturas, name='viaturas'),
    path('municoes/', views.dashboard_municoes, name='municoes'),
    path('estoque/', views.dashboard_estoque, name='estoque'),
    path('relatorios/', views.dashboard_relatorios, name='relatorios'),
    path('escalas/', views.dashboard_escalas, name='escalas'),
    path('apreendidos/', views.dashboard_apreendidos, name='apreendidos'),
    
    # API para dados AJAX
    path('api/chart/<str:chart_type>/', views.api_chart_data, name='api_chart'),
]
