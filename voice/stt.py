#!/usr/bin/env python3
"""
Script STT para Termux usando whisper.cpp CLI.
"""
import sys
import subprocess
from pathlib import Path

# Configuração
WHISPER_BIN = Path("/storage/shared/ai/cubot/whisper/main")
MODEL_PATH = Path("/storage/shared/ai/cubot/models/ggml-tiny.bin")

def transcribe(audio_path: str) -> str:
    """Transcreve áudio para texto."""
    if not WHISPER_BIN.exists():
        raise FileNotFoundError(f"whisper não encontrado: {WHISPER_BIN}")
    
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")
    
    cmd = [
        str(WHISPER_BIN),
        "-m", str(MODEL_PATH),
        "-f", audio_path,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.stdout.strip()

def main():
    if len(sys.argv) < 2:
        print("Uso: python stt.py <audio.wav>")
        sys.exit(1)
    
    try:
        text = transcribe(sys.argv[1])
        print(text)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()