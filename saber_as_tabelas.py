import os
import django

# Configure o Django manualmente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")  # Substitua pelo caminho para o seu settings.py
django.setup()

from django.db import connection

def get_all_tables():
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]

# Chamada da função
tabelas = get_all_tables()
print(tabelas)