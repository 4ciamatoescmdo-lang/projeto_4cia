FROM python:3.12-slim

WORKDIR /app

# dependências mínimas (você nem precisa de libpq-dev usando sqlite)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# dependências python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar projeto
COPY . .

# expor porta do Django
EXPOSE 8000

# comando padrão
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]