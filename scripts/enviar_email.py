#!/usr/bin/env python3
import os
import sys
import json
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def carregar_env():
    """Carrega as variáveis de ambiente do arquivo .env local sem usar bibliotecas externas."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    env_path = os.path.join(project_dir, ".env")
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue
                if "=" in linha:
                    chave, valor = linha.split("=", 1)
                    valor = valor.strip().strip('"').strip("'")
                    os.environ[chave.strip()] = valor

def obter_config_smtp():
    """Recupera as credenciais SMTP do ambiente."""
    carregar_env()
    return {
        "host": os.environ.get("SMTP_HOST"),
        "port": int(os.environ.get("SMTP_PORT", 587)),
        "user": os.environ.get("SMTP_USER"),
        "password": os.environ.get("SMTP_PASSWORD")
    }

def enviar_ata_por_email(anexo_path, membros_path, assunto_ata=None, dry_run=False):
    """Envia a ata (PDF ou DOCX) por e-mail para os membros cadastrados."""
    # Fallback se o PDF não existir mas o DOCX sim
    if not os.path.exists(anexo_path):
        base, ext = os.path.splitext(anexo_path)
        if ext.lower() == ".pdf":
            docx_path = base + ".docx"
            if os.path.exists(docx_path):
                print(f"Aviso: Arquivo PDF '{anexo_path}' não encontrado. Usando '{docx_path}' como fallback.")
                anexo_path = docx_path
            else:
                print(f"Erro: Nem o arquivo PDF '{anexo_path}' nem o Word '{docx_path}' foram localizados.")
                return False
        else:
            print(f"Erro: Arquivo de anexo '{anexo_path}' não localizado.")
            return False
        
    if not os.path.exists(membros_path):
        print(f"Erro: Banco de contatos '{membros_path}' não localizado.")
        return False
        
    # Carrega contatos
    with open(membros_path, "r", encoding="utf-8") as f:
        contatos = json.load(f)
        
    destinatarios = list(contatos.values())
    if not destinatarios:
        print("Erro: Nenhum e-mail localizado na base de contatos.")
        return False
        
    # Configurações do SMTP
    smtp_config = obter_config_smtp()
    
    # Valida credenciais ou força dry-run caso estejam em branco ou com placeholder
    if not smtp_config["host"] or not smtp_config["user"] or not smtp_config["password"]:
        print("Aviso: Configurações SMTP ausentes ou incompletas no arquivo .env.")
        print("Ativando modo simulado (dry-run). Nenhum e-mail real será enviado.")
        dry_run = True
    elif "exemplo" in smtp_config["user"] or "exemplo" in smtp_config["host"]:
        print("Aviso: Credenciais de exemplo detectadas no arquivo .env.")
        print("Ativando modo simulado (dry-run). Nenhum e-mail real será enviado.")
        dry_run = True

    # Assunto e corpo do e-mail
    titulo_reuniao = assunto_ata if assunto_ata else "Ata de Reunião"
    assunto = f"[Ata de Reunião] {titulo_reuniao}"
    
    corpo_html = f"""
    <html>
      <body style="font-family: 'Times New Roman', Times, serif; color: #2C2C2C; line-height: 1.6;">
        <h2 style="color: #4B2B7E;">Olá, Equipe TechTins!</h2>
        <p>Seguem em anexo as atas e decisões correspondentes à nossa última reunião: <strong>{titulo_reuniao}</strong>.</p>
        <p>Por favor, revisem os encaminhamentos e prazos descritos no documento em anexo.</p>
        <br>
        <hr style="border: 0; border-top: 1px solid #FED99B; width: 100%;">
        <p style="font-size: 11px; color: #787878;">
          Mensagem gerada de forma automática pelo <strong>Orquestrador de Atas (TechTins)</strong>.
        </p>
      </body>
    </html>
    """

    print(f"Preparando envio para os seguintes destinatários: {', '.join(destinatarios)}")
    
    if dry_run:
        print("\n--- SIMULAÇÃO DE ENVIO DE E-MAIL (DRY-RUN) ---")
        print(f"Remetente: {smtp_config['user'] if smtp_config['user'] else 'bot@techtins.com'}")
        print(f"Destinatários: {destinatarios}")
        print(f"Assunto: {assunto}")
        print(f"Anexo: {os.path.basename(pdf_path)}")
        print("Conteúdo:")
        print(corpo_html)
        print("---------------------------------------------\n")
        print("Simulação concluída com sucesso!")
        return True

    # Envio real
    try:
        # Monta a mensagem MIME
        msg = MIMEMultipart()
        msg["From"] = smtp_config["user"]
        msg["To"] = ", ".join(destinatarios)
        msg["Subject"] = assunto
        
        # Corpo
        msg.attach(MIMEText(corpo_html, "html"))
        
        # Anexo
        with open(pdf_path, "rb") as f:
                anexo = MIMEApplication(f.read(), _subtype="pdf")
            elif ext == ".docx":
                anexo = MIMEApplication(
                    f.read(),
                    _subtype="vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                anexo = MIMEApplication(f.read())
                
            anexo.add_header('Content-Disposition', 'attachment', filename=nome_arquivo)
            msg.attach(anexo)
            
        print(f"Conectando ao servidor SMTP {smtp_config['host']}:{smtp_config['port']}...")
        server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
        server.starttls()
        
        print("Efetuando login...")
        server.login(smtp_config["user"], smtp_config["password"])
        
        print("Enviando e-mail...")
        server.sendmail(smtp_config["user"], destinatarios, msg.as_string())
        server.quit()
        
        print("Sucesso! E-mails enviados com sucesso para todos os membros.")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar e-mail via SMTP: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Distribui o arquivo PDF da ata para todos os e-mails da Empresa Júnior cadastrados no sistema."
    )
    parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo da ata (PDF ou Word).")
    parser.add_argument("-c", "--config", default="config/membros.json", help="Caminho para o arquivo de membros (membros.json).")
    parser.add_argument("-t", "--title", help="Título descritivo da reunião (para compor o assunto).")
    parser.add_argument("--dry-run", action="store_true", help="Executa uma simulação sem disparar e-mails reais.")
    
    args = parser.parse_args()
    
    sucesso = enviar_ata_por_email(args.input, args.config, args.title, args.dry_run)
    if not sucesso:
        sys.exit(1)

if __name__ == "__main__":
    main()
