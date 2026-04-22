@echo off
title Servidor Django - 4ª CIA PM
color 0A

echo ========================================
echo    Iniciando Servidor Django - 4ª CIA
echo ========================================
echo.

:: 1. Encerrar qualquer processo na porta 8000
echo [1/5] Verificando processos na porta 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo      Encerrando processo PID: %%a
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul
echo      [+] Porta 8000 liberada!
echo.

:: 2. Ativar ambiente virtual (.venv)
echo [2/5] Ativando ambiente virtual...
cd /d "C:\Users\TCO\Downloads\GITHUB\aplicativo_4cia_2026_1-main\aplicativo_4cia_2026_1-main"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo      [+] Ambiente .venv ativado com sucesso!
) else (
    echo      [ERRO] Ambiente virtual nao encontrado em: .venv
    echo      Pasta atual: %cd%
    pause
    exit /b 1
)
echo.

:: 3. Entrar na pasta do projeto Django
echo [3/5] Acessando pasta do projeto...
cd projeto4cia
echo      [+] Pasta: %cd%
echo.

:: 4. Verificar Django e dependências (opcional)
echo [4/5] Verificando instalacao do Django...
python -c "import django" 2>nul
if errorlevel 1 (
    echo      [AVISO] Django nao encontrado!
    echo      Instalando dependencias do requirements.txt...
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        echo      [ERRO] Arquivo requirements.txt nao encontrado!
        echo      Por favor, instale o Django manualmente: pip install django
        pause
        exit /b 1
    )
) else (
    echo      [+] Django OK!
)
echo.

:: 5. Executar migrations (garantir banco atualizado)
echo [5/5] Verificando migracoes pendentes...
python manage.py migrate --noinput 2>nul
echo      [+] Banco de dados sincronizado!
echo.

:: 6. Iniciar servidor Django
echo.
echo ========================================
echo    Servidor iniciado com sucesso!
echo    URL: http://127.0.0.1:8000
echo    Pressione CTRL+C para parar o servidor
echo ========================================
echo.

:: Abrir navegador automaticamente após 2 segundos
start http://127.0.0.1:8000

:: Executar o servidor
python manage.py runserver

:: Se chegar aqui, o servidor foi encerrado
echo.
echo ========================================
echo    Servidor encerrado!
echo ========================================
timeout /t 3 /nobreak >nul