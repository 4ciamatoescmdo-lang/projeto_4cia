from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'autenticacao'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='autenticacao/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Opcional: trocar senha
    path('trocar-senha/', auth_views.PasswordChangeView.as_view(
        template_name='autenticacao/trocar_senha.html',
        success_url='/'
    ), name='trocar_senha'),
]