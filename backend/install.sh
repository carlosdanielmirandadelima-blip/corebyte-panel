#!/bin/bash
# Script de instalação CubotAI no Termux
# Execute: bash install.sh

set -e

echo "============================================"
echo "Instalando CubotAI - Termux"
echo "============================================"

# Atualizar
pkg update && pkg upgrade -y

# Dependências mínimas
pkg install -y python git wget curl termux-api

# Criar diretório
mkdir -p ~/cubot-ai
cd ~/cubot-ai

# ============================================================
# 下载 modelo GGUF Qwen
# ============================================================
echo "Baixando modelo Qwen 2.5 1.5B..."
mkdir -p models
cd models

# URL direta HuggingFace (use gh ou wget com token)
wget -O qwen2.5-1.5b-instruct-q4_k_m.gguf \
    "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf" \
    || echo "Baixue manualmente em: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF"

# ============================================================
# 下载 llama.cpp binário ARM64
# ============================================================
echo "Baixando llama.cpp binário..."
cd ~/cubot-ai
mkdir -p llama.cpp

# Download binário pré-compilado ARM64
wget -O llama.cpp/main \
    "https://github.com/ggerganov/llama.cpp/releases/download/b3655/llama.cpp-bin-arm64-v8a-vllm-v0" \
    || wget -O llama.cpp/main \
    "https://github.com/ggerganov/llama.cpp/releases/download/b3655/llama-android-arm64" \
    || echo "Baixue manualmente de: https://github.com/ggerganov/llama.cpp/releases"

chmod +x llama.cpp/main

echo "============================================"
echo "Instalação concluída!"
echo "============================================"
echo ""
echo "Para iniciar:"
echo "  cd ~/cubot-ai"
echo "  python backend/main.py"
echo ""
echo "O servidor estará em: http://localhost:5000"