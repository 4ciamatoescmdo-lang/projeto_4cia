
from pathlib import Path
import os
# from dotenv import load_dotenv

# Try to import dj_database_url dynamically; if it's not installed, fall back to None
# and use a default sqlite configuration below.
try:
    import importlib
    dj_database_url = importlib.import_module('dj_database_url')
except Exception:
    dj_database_url = None

# load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = "django-insecure-fsbg504$gg5vzw_-$w6sm#+m%-n7hrkyaem6rb8!!zv-^vv6s_"
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-sua-chave-temporaria')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django_extensions',
    'aplicacoes.cadastros.cadastro_policiais',  # <-- VERIFIQUE SE TEM VÍRGULA AQUI
    'aplicacoes.seguranca.autenticacao',    
    'aplicacoes.cadastros.cadastro_vtrs',
    'aplicacoes.cadastros.cadastro_armamentos',      # <-- NOVA
    'aplicacoes.cadastros.cadastro_equipamentos',    # <-- NOVA
    'aplicacoes.cadastros.cadastro_eletronicos',     # <-- NOVA
    'aplicacoes.cadastros.cadastro_mobilia',         # <-- NOVA
    'aplicacoes.cautela_e_descautela.cautela_armamento.apps.CautelaArmamentoConfig',  # <-- Corrigido
    'aplicacoes.cadastros.cadastro_municoes.apps.CadastroMunicoesConfig',  # <-- NOVA
    'aplicacoes.livros.livro_diario.apps.LivroDiarioConfig',  # <-- NOVA
    'aplicacoes.livros.livro_de_cautela.apps.LivroDeCautelaConfig',  # <-- NOVA
    'aplicacoes.cadastros.cadastro_comandante.apps.CadastroComandanteConfig',  # <-- NOVA
    'aplicacoes.cadastros.cadastro_veiculo_apreendido.apps.CadastroVeiculoApreendidoConfig',  # <-- NOVA
    'aplicacoes.escala_diaria',
    'aplicacoes.relatorio_analitico',
    'aplicacoes.dashboard',  # <-- NOVA

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "base.middleware.SessionTimeoutMiddleware",
]

ROOT_URLCONF = "base.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'base' / 'templates',
                 BASE_DIR / 'aplicacoes' / 'seguranca' / 'templates',
                 BASE_DIR / 'aplicacoes' / 'cadastros' / 'templates',
                 BASE_DIR / 'aplicacoes' / 'relatorio_analitico' / 'templates'],
        
        
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "base.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# DATABASES = {
#     "default": {
# }
# Configure DATABASES: use dj_database_url if available, otherwise fall back to sqlite.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# if dj_database_url:
#     DATABASES = {
#         'default': dj_database_url.config(
#             default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
#             conn_max_age=600
#         )
#     }
# else:
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.sqlite3",
#             "NAME": BASE_DIR / "db.sqlite3",
#         }
#     }

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "aplicacoes" / "livros" / "livro_de_cautela" / "static",
    BASE_DIR / "aplicacoes" / "cadastros" / "cadastro_veiculo_apreendido" / "static",
    BASE_DIR / 'base' / 'static',  # <-- Para CSS/JS customizados
    BASE_DIR / 'aplicacoes' / 'escala_diaria' / 'static',
    BASE_DIR / 'aplicacoes' / 'relatorio_analitico' / 'static',
    BASE_DIR / 'aplicacoes' / 'seguranca' / 'autenticacao' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configurações de autenticação
LOGIN_URL = 'autenticacao:login'  # Adicione o namespace
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'  # Use URL direta em vez de nome

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configurações de mensagens (para feedback ao usuário)
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.INFO: 'info',
}


# Adicione no final do seu settings.py

# Configuração de sessão - tempo de expiração em segundos (5 minutos = 300 segundos)
SESSION_COOKIE_AGE = 300  # 5 minutos em segundos

# Forçar o navegador a enviar o cookie de sessão apenas em conexões HTTPS (recomendado para produção)
SESSION_COOKIE_SECURE = False  # Mude para True em produção com HTTPS

# Impedir que o JavaScript acesse o cookie de sessão (segurança)
SESSION_COOKIE_HTTPONLY = True

# Renovar o cookie de sessão a cada requisição (mantém a sessão ativa enquanto o usuário interage)
SESSION_SAVE_EVERY_REQUEST = True

# Fechar a sessão quando o navegador for fechado (junto com o tempo)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'