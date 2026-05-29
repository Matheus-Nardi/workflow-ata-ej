#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse

def converter_docx_para_pdf(input_path, output_dir=None):
    """Converte um arquivo .docx para .pdf usando LibreOffice Headless."""
    if not os.path.exists(input_path):
        print(f"Erro: Arquivo de entrada '{input_path}' não existe.")
        return False

    input_path = os.path.abspath(input_path)
    if not output_dir:
        output_dir = os.path.dirname(input_path)
    else:
        output_dir = os.path.abspath(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Convertendo '{input_path}' para PDF...")
    try:
        # Comando do LibreOffice para conversão headless
        comando = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            input_path
        ]
        
        # Executa o comando
        resultado = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        # O nome do arquivo gerado pelo LibreOffice é igual ao original mas com extensão .pdf
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        
        if os.path.exists(pdf_path):
            print(f"Sucesso! PDF gerado e salvo em '{pdf_path}'.")
            return pdf_path
        else:
            print("Erro: O LibreOffice indicou sucesso, mas o arquivo PDF não foi localizado.")
            print(resultado.stdout)
            return False
            
    except subprocess.CalledProcessError as e:
        print("Erro ao executar a conversão com o LibreOffice:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("Erro: O comando 'libreoffice' não foi localizado no sistema.")
        print("Certifique-se de que o LibreOffice está instalado e disponível no PATH.")
        return False
    except Exception as e:
        print(f"Erro inesperado durante a conversão: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Converte arquivos Word (.docx) para PDF usando o LibreOffice de forma headless."
    )
    parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo .docx de entrada.")
    parser.add_argument("-o", "--output-dir", help="Diretório onde o PDF gerado será salvo (opcional).")
    
    args = parser.parse_args()
    
    pdf_criado = converter_docx_para_pdf(args.input, args.output_dir)
    if not pdf_criado:
        sys.exit(1)

if __name__ == "__main__":
    main()
