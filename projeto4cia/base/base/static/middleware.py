# base/middleware.py
from datetime import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
import logging

logger = logging.getLogger(__name__)

class SessionTimeoutMiddleware:
    """
    Middleware para expirar sessão após 5 minutos de inatividade
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verifica se o usuário está autenticado
        if request.user.is_authenticated:
            # Ignorar URLs de autenticação
            ignore_paths = ['/auth/login/', '/auth/logout/', '/admin/login/']
            if request.path not in ignore_paths:
                
                # Tempo máximo de inatividade (5 minutos)
                max_inactive_time = 300  # segundos
                
                # Pega o último acesso da sessão
                last_activity = request.session.get('last_activity')
                current_time = datetime.now()
                
                if last_activity:
                    # Se last_activity for string, converte para datetime
                    if isinstance(last_activity, str):
                        try:
                            from dateutil import parser
                            last_activity = parser.parse(last_activity)
                        except:
                            # Se não conseguir converter, usa o formato ISO
                            last_activity = datetime.fromisoformat(last_activity)
                    
                    # Calcula tempo inativo
                    inactive_seconds = (current_time - last_activity).total_seconds()
                    
                    if inactive_seconds > max_inactive_time:
                        # Sessão expirada
                        logger.info(f'Sessão expirada para {request.user.username}')
                        logout(request)
                        request.session.flush()
                        return redirect('autenticacao:login')
                
                # Atualiza último acesso
                request.session['last_activity'] = current_time.isoformat()
        
        response = self.get_response(request)
        return response