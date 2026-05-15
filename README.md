# CubotAI - Assistente de IA Local

## O que é
Assistente de IA offline para Android (Cubot X70).

## Stack
- Python 3.11+ (http.server nativo)
- SQLite (memória)
- llama.cpp binário (inferência)
- Qwen 2.5 1.5B GGUF

## Arquitetura
```
backend/main.py  -> Servidor HTTP (python nativo)
memory          -> SQLite (arquivo local)
voice/stt.py    -> whisper.cpp CLI
automation     -> Tasker/MacroDroid
```

## Instalação
Veja em: `docs/INSTALL.md`

## API
| Endpoint | Método | Função |
|----------|--------|--------|
| /health | GET | Status |
| /chat | POST | Chat |
| /clear | POST | Limpar sessão |
| /model/info | GET | Info modelo |

## Uso
```bash
# Servidor
python backend/main.py

# Chat
curl -X POST http://localhost:5000/chat \
  -d '{"message": "Olá"}'
```