# CubotAI - Instalação Completa no Termux

## Requisitos
- Cubot X70 (Helio G99, 12GB RAM)
- Termux instalado
- ~2GB armazenamento livre

---

## Passo 1: Instalar Termux

Baixe em: https://f-droid.org/packages/com.termux/

---

## Passo 2: Comandos de Instalação

Copie e execute no Termux:

```bash
# Criar diretório
mkdir -p ~/cubot-ai
cd ~/cubot-ai

# Instalação mínima
pkg update && pkg upgrade -y
pkg install -y python git wget curl termux-api

# Baixar projeto
git clone https://github.com/carlosdanielmirandadelima-blip/Ia-cubot.git .

# ou baixe o ZIP e extraia
```

---

## Passo 3: Baixar Modelos

### Qwen GGUF (~1.7GB)
```bash
cd ~/cubot-ai/models

# Método 1: wget (pode falhar)
wget -O qwen2.5-1.5b-instruct-q4_k_m.gguf \
    "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

# Método 2: Use o app "Download Helium" ou "IDM" no Android
# Acesse: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
# Baixe o arquivo qwen2.5-1.5b-instruct-q4_k_m.gguf
# Copie para /storage/shared/ai/cubot/models/
```

### llama.cpp binário

Não disponível pré-compilado para Android diretamente. Use alternativa:

```bash
# Opção 1: Compilar leve (requer clang, ~10 min)
cd ~/cubot-ai
pkg install -y clang cmake make llvm

git clone --depth 1 https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4

# O binário estará em build/main
cp build/main ~/cubot-ai/llama.cpp/main
```

---

## Passo 4: Configurar

```bash
# Criar diretório de dados
mkdir -p /storage/shared/ai/cubot/models
mkdir -p /storage/shared/ai/cubot/llama.cpp

# Copiar modelos para lá
# (use Gerenciador de Arquivos ou ADB)

# Criar banco de dados
touch /storage/shared/ai/cubot/memory.db
```

---

## Passo 5:Iniciar Servidor

```bash
cd ~/cubot-ai
python backend/main.py
```

O servidor vai iniciar em http://localhost:5000

---

## Passo 6: Testar

```bash
# Verificar status
curl http://localhost:5000/health

# Testar chat
curl -X POST http://localhost:5000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Olá", "session_id": "test"}'
```

---

## Estrutura de Arquivos

```
~/cubot-ai/
├── backend/
│   ├── main.py       # Servidor
│   └── install.sh    # Script install
├── models/
│   └── qwen2.5-1.5b-instruct-q4_k_m.gguf
├── llama.cpp/
│   └── main         # Binário
└── memory.db        # SQLite

/storage/shared/ai/cubot/
├── models/
│   └── qwen2.5-1.5b-instruct-q4_k_m.gguf
├── llama.cpp/
│   └── main
└── memory.db
```

---

## Comandos Rápidos

```bash
# Iniciar
cd ~/cubot-ai && python backend/main.py

# Parar
pkill -f "python backend/main.py"

# Verificar se está rodando
curl http://localhost:5000/health

# Logs
logcat | grep python
```

---

## Solução de Problemas

### "llama.cpp main não encontrado"
- Compile ou baixe o binário
- Verifique o caminho em LLAMA_BIN

### "Modelo não encontrado"
- Baixe o modelo GGUF
- Verifique o caminho em MODEL_PATH

### "Porta em uso"
- Mude a porta em main.py
- Ou kill o processo

### "Out of memory"
- Reduza MAX_TOKENS para 128
- Reduza CONTEXT_SIZE para 1024
- Reduza N_THREADS para 2