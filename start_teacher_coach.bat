@echo off
title Teacher Coach AI - Setup
color 0B

echo ========================================================
echo   Select Language / Seleccione el Idioma
echo ========================================================
echo 1. English
echo 2. Espanol
echo 3. Portugues
echo 4. Francais
echo.
set /p lang="Choice / Opcion (1/2/3/4): "

if "%lang%"=="1" goto english
if "%lang%"=="2" goto spanish
if "%lang%"=="3" goto portuguese
if "%lang%"=="4" goto french
goto english

:english
set MSG_START=Starting Teacher Coach AI (Offline Mode)
set MSG_ERR_PY=[ERROR] Python is not installed or not in PATH. Please install Python 3.9+ before continuing.
set MSG_ERR_OLLAMA=[ERROR] Ollama is not installed or not running. Please download from https://ollama.com.
set MSG_STEP1=[1/3] Installing dependencies...
set MSG_STEP2=[2/3] Verifying AI model (gemma4:e2b)...
set MSG_STEP3=[3/3] Starting local Streamlit server...
set MSG_WARN=The browser will open automatically. Do not close this terminal.
goto run_app

:spanish
set MSG_START=Iniciando Teacher Coach AI (Modo Offline)
set MSG_ERR_PY=[ERROR] Python no esta instalado o no esta en el PATH. Por favor instala Python 3.9+ antes de continuar.
set MSG_ERR_OLLAMA=[ERROR] Ollama no esta instalado o no se esta ejecutando. Por favor descarga desde https://ollama.com.
set MSG_STEP1=[1/3] Instalando dependencias...
set MSG_STEP2=[2/3] Verificando modelo de IA (gemma4:e2b)...
set MSG_STEP3=[3/3] Levantando el servidor local...
set MSG_WARN=El navegador se abrira automaticamente. No cierres esta terminal.
goto run_app

:portuguese
set MSG_START=Iniciando Teacher Coach AI (Modo Offline)
set MSG_ERR_PY=[ERRO] Python nao esta instalado. Por favor instale o Python 3.9+ antes de continuar.
set MSG_ERR_OLLAMA=[ERRO] Ollama nao esta instalado ou nao esta rodando. Baixe em https://ollama.com.
set MSG_STEP1=[1/3] Instalando dependencias...
set MSG_STEP2=[2/3] Verificando modelo de IA (gemma4:e2b)...
set MSG_STEP3=[3/3] Iniciando servidor local...
set MSG_WARN=O navegador abrira automaticamente. Nao feche este terminal.
goto run_app

:french
set MSG_START=Demarrage de Teacher Coach AI (Mode Hors Ligne)
set MSG_ERR_PY=[ERREUR] Python n'est pas installe. Veuillez installer Python 3.9+ avant de continuer.
set MSG_ERR_OLLAMA=[ERREUR] Ollama n'est pas installe ou ne s'execute pas. Telechargez depuis https://ollama.com.
set MSG_STEP1=[1/3] Installation des dependances...
set MSG_STEP2=[2/3] Verification du modele IA (gemma4:e2b)...
set MSG_STEP3=[3/3] Demarrage du serveur local...
set MSG_WARN=Le navigateur s'ouvrira automatiquement. Ne fermez pas ce terminal.
goto run_app

:run_app
cls
echo ========================================================
echo        %MSG_START%
echo ========================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %MSG_ERR_PY%
    pause
    exit /b
)

ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %MSG_ERR_OLLAMA%
    pause
    exit /b
)

echo %MSG_STEP1%
pip install -r requirements.txt -q

echo %MSG_STEP2%
ollama pull gemma4:e2b

echo %MSG_STEP3%
echo %MSG_WARN%
echo.
streamlit run app.py

pause
