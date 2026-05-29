#!/usr/bin/env python3
import os
import sys
import json
import argparse

# Garante o import local do db_atas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import db_atas

def main():
    parser = argparse.ArgumentParser(
        description="Registra uma ata no banco SQLite, obtendo número sequencial e ano/semestre, atualizando o arquivo JSON."
    )
    parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo JSON da ata estruturada.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Erro: Arquivo de entrada '{args.input}' não encontrado.")
        sys.exit(1)
        
    # 1. Carrega o JSON da ata
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        print(f"Erro ao ler arquivo JSON '{args.input}': {e}")
        sys.exit(1)
        
    data_reuniao = dados.get("data")
    titulo = dados.get("titulo")
    
    if not data_reuniao or not titulo:
        print("Erro: O JSON fornecido precisa conter obrigatoriamente os campos 'data' (YYYY-MM-DD) e 'titulo'.")
        sys.exit(1)
        
    caminho_absoluto_json = os.path.abspath(args.input)
    
    # 2. Registra no banco SQLite e obtém a numeração correta
    try:
        numero, ano, semestre = db_atas.obter_ou_criar_registro_ata(
            data_reuniao=data_reuniao,
            titulo=titulo,
            caminho_json=caminho_absoluto_json
        )
    except Exception as e:
        print(f"Erro ao interagir com o banco de dados SQLite: {e}")
        sys.exit(1)
        
    # 3. Adiciona os metadados calculados ao dicionário JSON
    dados["numero"] = numero
    dados["ano"] = ano
    dados["semestre"] = semestre
    
    # 4. Salva o JSON atualizado de volta no mesmo arquivo
    try:
        with open(args.input, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        print(f"Sucesso! JSON da ata atualizado com a numeração oficial da ata (Nº {numero:02d} / {ano}.{semestre}).")
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON atualizado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
