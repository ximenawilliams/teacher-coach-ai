#!/bin/bash

echo "========================================================"
echo "  Select Language / Seleccione el Idioma"
echo "========================================================"
echo "1. English"
echo "2. Español"
echo ""
read -p "Choice / Opción (1/2): " lang

if [ "$lang" == "2" ]; then
    MSG_START="Iniciando Teacher Coach AI (Offline Mode)"
    MSG_ERR_PY="[ERROR] Python3 no está instalado. Por favor instálalo antes de continuar."
    MSG_ERR_OLLAMA="[ERROR] Ollama no está instalado. Por favor descárgalo en https://ollama.com"
    MSG_STEP1="[1/3] Instalando dependencias necesarias..."
    MSG_STEP2="[2/3] Verificando modelo de inteligencia artificial (gemma4:e2b)..."
    MSG_STEP3="[3/3] Levantando el servidor local de Streamlit..."
else
    MSG_START="Starting Teacher Coach AI (Offline Mode)"
    MSG_ERR_PY="[ERROR] Python3 is not installed. Please install it before continuing."
    MSG_ERR_OLLAMA="[ERROR] Ollama is not installed. Please download it from https://ollama.com"
    MSG_STEP1="[1/3] Installing necessary dependencies..."
    MSG_STEP2="[2/3] Verifying AI model (gemma4:e2b)..."
    MSG_STEP3="[3/3] Starting local Streamlit server..."
fi

clear
echo "========================================================"
echo "        $MSG_START"
echo "========================================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "$MSG_ERR_PY"
    exit 1
fi

if ! command -v ollama &> /dev/null; then
    echo "$MSG_ERR_OLLAMA"
    exit 1
fi

echo "$MSG_STEP1"
pip3 install -r requirements.txt -q

echo "$MSG_STEP2"
ollama pull gemma4:e2b

echo "$MSG_STEP3"
streamlit run app.py
