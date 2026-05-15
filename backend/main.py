#!/usr/bin/env python3
"""
Backend minimalista para CubotAI no Termux.
Usa llama.cpp binário externo via subprocess.
"""
import os
import sys
import json
import subprocess
import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path("/storage/shared/ai/cubot")
MODEL_PATH = BASE_DIR / "models" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
LLAMA_BIN = BASE_DIR / "llama.cpp" / "main"
DB_PATH = BASE_DIR / "memory.db"

# Criar diretórios
BASE_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

CONTEXT_SIZE = 2048
MAX_TOKENS = 256  # Reduzido para estabilidade
N_THREADS = 4

# ============================================================
# BANCO DE DADOS
# ============================================================

def init_db():
    """Inicializa banco SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                session_id TEXT,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)")
        conn.commit()

def add_message(session_id: str, role: str, content: str):
    """Adiciona mensagem ao banco."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()

def get_context(session_id: str, limit: int = 8) -> str:
    """Obtém contexto recente."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """SELECT role, content FROM messages 
               WHERE session_id = ? ORDER BY created_at DESC LIMIT ?""",
            (session_id, limit)
        )
        rows = cur.fetchall()
    
    lines = []
    for row in reversed(rows):
        prefix = "Usuário" if row[0] == "user" else "Assistente"
        lines.append(f"{prefix}: {row[1]}")
    return "\n".join(lines)

def clear_session(session_id: str):
    """Limpa sessão."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()

# ============================================================
# INFERÊNCIA GGUF via subprocess
# ============================================================

def generate(prompt: str, system_prompt: str = "") -> str:
    """Gera resposta usando llama.cpp binário."""
    if not LLAMA_BIN.exists():
        raise FileNotFoundError(f"llama.cpp não encontrado: {LLAMA_BIN}")
    
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")
    
    # Construir prompt no formato Qwen
    full_prompt = build_prompt(prompt, system_prompt)
    
    # Salvar em arquivo temporário
    prompt_file = BASE_DIR / "prompt.txt"
    prompt_file.write_text(full_prompt)
    
    # Comando llama.cpp
    cmd = [
        str(LLAMA_BIN),
        "-m", str(MODEL_PATH),
        "-f", str(prompt_file),
        "-n", str(MAX_TOKENS),
        "--threads", str(N_THREADS),
        "-c", str(CONTEXT_SIZE),
        "--no-mmap",
    ]
    
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        response = result.stdout.strip()
        
        # Limpar arquivo temporário
        prompt_file.unlink(missing_ok=True)
        
        return response if response else "Desculpe, não consegui gerar resposta."
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("Tempo limite excedido.")
    except Exception as e:
        raise RuntimeError(f"Erro: {e}")

def build_prompt(user_prompt: str, system_prompt: str) -> str:
    """Constrói prompt no formato Qwen."""
    lines = []
    if system_prompt:
        lines.append(f"<|system|>\n{system_prompt}")
    lines.append(f"<|user|>\n{user_prompt}")
    lines.append("<|assistant|>\n")
    return "\n".join(lines)

# ============================================================
# HTTP SERVER SIMPLES
# ============================================================

class Handler(BaseHTTPRequestHandler):
    """Handler HTTP simples."""
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        """GET requests."""
        if self.path == "/" or self.path == "/health":
            self.send_json({"status": "ok", "model_loaded": MODEL_PATH.exists()})
        elif self.path == "/model/info":
            self.send_json({
                "model": str(MODEL_PATH),
                "exists": MODEL_PATH.exists()
            })
        else:
            self.send_error(404)
    
    def do_POST(self):
        """POST requests."""
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length > 0 else ""
        
        if self.path == "/chat":
            try:
                data = json.loads(body)
                msg = data.get("message", "")
                session = data.get("session_id", "default")
                system = data.get("system_prompt", "")
                
                # Obter contexto
                ctx = get_context(session)
                if ctx:
                    system = system + "\n\nContexto:\n" + ctx
                
                # Gerar resposta
                response = generate(msg, system)
                
                # Salvar
                add_message(session, "user", msg)
                add_message(session, "assistant", response)
                
                self.send_json({"response": response, "session_id": session})
                
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
        
        elif self.path == "/clear":
            try:
                data = json.loads(body)
                session = data.get("session_id", "default")
                clear_session(session)
                self.send_json({"status": "cleared", "session_id": session})
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
        
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        """Envia JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

# ============================================================
# MAIN
# ============================================================

def main():
    """Inicia servidor."""
    init_db()
    
    port = 5000
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"CubotAI rodando em http://0.0.0.0:{port}")
    print(f"Modelo: {MODEL_PATH}")
    print(f"llama.cpp: {LLAMA_BIN}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando...")
        server.shutdown()

if __name__ == "__main__":
    main()