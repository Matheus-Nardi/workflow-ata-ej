#!/usr/bin/env python3
import os
import sys
import argparse
import requests

def transcrever_audio(audio_path, output_path, api_key):
    if not os.path.exists(audio_path):
        print(f"Erro: O arquivo de áudio '{audio_path}' não foi encontrado.")
        sys.exit(1)
        
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepara o arquivo de áudio para envio multipart/form-data
    print(f"Enviando '{audio_path}' para a API do Groq (Whisper Large)...")
    try:
        # Determina o mime type apropriado a partir da extensão
        ext = os.path.splitext(audio_path)[1].lower()
        mime_types = {
            ".mp3": "audio/mpeg",
            ".mp4": "audio/mp4",
            ".m4a": "audio/mp4",
            ".wav": "audio/wav",
            ".mpeg": "audio/mpeg",
            ".webm": "audio/webm"
        }
        mime_type = mime_types.get(ext, "application/octet-stream")

        with open(audio_path, "rb") as f:
            files = {
                "file": (os.path.basename(audio_path), f, mime_type)
            }
            data = {
                "model": "whisper-large-v3",
                "language": "pt"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
        if response.status_code == 200:
            resultado = response.json()
            texto_transcrito = resultado.get("text", "")
            
            # Garante que o diretório de destino existe
            diretorio_destino = os.path.dirname(os.path.abspath(output_path))
            os.makedirs(diretorio_destino, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as out:
                out.write(texto_transcrito)
                
            print(f"Sucesso! Transcrição salva em '{output_path}'.")
            print(f"Total de caracteres transcritos: {len(texto_transcrito)}")
        else:
            print(f"Erro na API do Groq: Código de status {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"Ocorreu um erro durante a transcrição: {e}")
        sys.exit(1)

def main():
    # Carrega variáveis do arquivo .env se ele existir (sem dependências externas)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

    parser = argparse.ArgumentParser(description="Transcreve áudio de reuniões usando a API do Groq (Whisper Large).")
    parser.add_argument("-i", "--input", default="audio_reuniao.mp3", help="Caminho para o arquivo de áudio de entrada (padrão: audio_reuniao.mp3)")
    parser.add_argument("-o", "--output", default="transcricao.txt", help="Caminho para o arquivo de texto de saída (padrão: transcricao.txt)")
    parser.add_argument("-k", "--key", help="Chave de API do Groq (ou defina a variável de ambiente GROQ_API_KEY)")
    
    args = parser.parse_args()
    
    # Resolve a API Key
    api_key = args.key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Erro: A chave de API do Groq não foi fornecida.")
        print("Defina a variável de ambiente GROQ_API_KEY ou use o parâmetro -k/--key.")
        sys.exit(1)
        
    transcrever_audio(args.input, args.output, api_key)

if __name__ == "__main__":
    main()
