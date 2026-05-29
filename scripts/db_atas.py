#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime

DB_NAME = "atas.db"

def obter_conexao():
    """Retorna uma conexão ativa com o banco SQLite."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    db_path = os.path.join(project_dir, DB_NAME)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    """Cria a tabela de atas caso ela não exista."""
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            semestre INTEGER NOT NULL,
            data_reuniao TEXT NOT NULL,
            titulo TEXT NOT NULL,
            caminho_json TEXT,
            caminho_docx TEXT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(numero, ano, semestre)
        );
    """)
    conn.commit()
    conn.close()

def obter_ou_criar_registro_ata(data_reuniao, titulo, caminho_json=None, caminho_docx=None):
    """
    Busca se a ata com a mesma data e título já foi registrada.
    Caso sim, atualiza seus caminhos e retorna os dados existentes (evita duplicar).
    Caso não, calcula o semestre, obtém o próximo número sequencial e insere um novo registro.
    """
    inicializar_banco()
    
    # 1. Extrair ano e semestre
    try:
        dt = datetime.strptime(data_reuniao, "%Y-%m-%d")
    except ValueError:
        # Fallback caso a data venha em formato diferente
        try:
            dt = datetime.strptime(data_reuniao, "%d/%m/%Y")
        except ValueError:
            dt = datetime.now()
            
    ano = dt.year
    semestre = 1 if dt.month <= 6 else 2
    
    conn = obter_conexao()
    cursor = conn.cursor()
    
    # 2. Verificar se já existe registro com a mesma data e título
    cursor.execute(
        "SELECT numero, ano, semestre FROM atas WHERE data_reuniao = ? AND titulo = ?",
        (data_reuniao, titulo)
    )
    resultado = cursor.fetchone()
    
    if resultado:
        numero = resultado["numero"]
        # Atualiza caminhos caso tenham mudado
        cursor.execute(
            "UPDATE atas SET caminho_json = COALESCE(?, caminho_json), caminho_docx = COALESCE(?, caminho_docx) WHERE data_reuniao = ? AND titulo = ?",
            (caminho_json, caminho_docx, data_reuniao, titulo)
        )
        conn.commit()
        conn.close()
        print(f"Registro de ata existente encontrado: Ata nº {numero:02d}/{ano}.{semestre}")
        return numero, ano, semestre

    # 3. Se não existe, calcula o próximo número
    cursor.execute(
        "SELECT MAX(numero) as max_num FROM atas WHERE ano = ? AND semestre = ?",
        (ano, semestre)
    )
    max_num_row = cursor.fetchone()
    proximo_numero = 1
    if max_num_row and max_num_row["max_num"] is not None:
        proximo_numero = max_num_row["max_num"] + 1
        
    # 4. Insere o novo registro
    cursor.execute(
        """
        INSERT INTO atas (numero, ano, semestre, data_reuniao, titulo, caminho_json, caminho_docx)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (proximo_numero, ano, semestre, data_reuniao, titulo, caminho_json, caminho_docx)
    )
    conn.commit()
    conn.close()
    
    print(f"Nova ata registrada com sucesso: Ata nº {proximo_numero:02d}/{ano}.{semestre}")
    return proximo_numero, ano, semestre

if __name__ == "__main__":
    # Teste rápido de inicialização do banco ao rodar o script diretamente
    inicializar_banco()
    print("Banco de dados SQLite inicializado com sucesso!")
