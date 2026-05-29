#!/usr/bin/env python3
import os
import sys
import json
import argparse
import requests

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
                    # Remove aspas se houver
                    valor = valor.strip().strip('"').strip("'")
                    os.environ[chave.strip()] = valor

def obter_api_key(args):
    """Retorna a chave da API do Groq do argumento ou do ambiente."""
    if args.key:
        return args.key
    carregar_env()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Erro: Chave de API do Groq não encontrada.")
        print("Defina a variável de ambiente GROQ_API_KEY ou crie um arquivo .env")
        sys.exit(1)
    return api_key

def estruturar_com_groq(markdown_content, schema_content, api_key):
    """Envia o markdown e o schema para a API do Groq para obter a estrutura JSON."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt_sistema = (
        "Você é um analisador e estruturador de dados experiente.\n"
        "Seu objetivo é ler uma ata de reunião em Markdown e transformá-la em um objeto JSON válido,\n"
        "respeitando estritamente o JSON Schema fornecido.\n\n"
        "Regras cruciais:\n"
        "1. Retorne APENAS o JSON puro. Não insira blocos de código markdown (como ```json) ou qualquer explicação.\n"
        "2. Certifique-se de que a data está no formato YYYY-MM-DD. Se a data fornecida for 28/05/2026, converta para '2026-05-28'.\n"
        "3. Mapeie todas as seções obrigatórias (titulo, data, local, participantes, resumo_assuntos, encaminhamentos, duvidas_incertezas, texto_corrido) e, caso exista na ata em Markdown, a seção opcional de 'Status de Desenvolvimento' (mapeada para a chave 'status_desenvolvimento').\n"
        "4. Na tabela de encaminhamentos, preencha acao, responsavel e prazo de cada item.\n"
        "5. O campo 'texto_corrido' DEVE ser redigido seguindo estritamente as regras de ata legal e burocrática:\n"
        "   - Preâmbulo Burocrático: O texto deve iniciar obrigatoriamente descrevendo a data, o horário, o local e o nome de todos os participantes presentes. A data, o ano e o horário devem ser escritos inteiramente por extenso. Exemplo: 'Aos vinte e nove dias do mês de maio de dois mil e vinte e seis, às dez horas, na sala do ESC da Universidade Estadual do Tocantins, reuniram-se...' seguido da lista de participantes separados por vírgula.\n"
        "   - Texto Contínuo: O texto corre do início ao fim sem qualquer quebra de linha (sem '\\n'), sem marcadores de tópicos (como hifens ou asteriscos no início de linhas) e sem recuos ou parágrafos. Tudo é um único e imenso bloco.\n"
        "   - Articulação e Transição de Assuntos (Sem Negrito): O texto deve ser inteiramente em texto plano, sem qualquer marcação de negrito (NÃO use '**'). Articule a transição de assuntos, encaminhamentos e dúvidas de forma discursiva, usando termos literais por extenso, tais como: 'na pauta número um...', 'com relação à pauta número dois...', 'como encaminhamento número um...', 'como encaminhamento número dois...', 'como primeira dúvida/incerteza...'. Todos os ordinais e cardinais devem ser escritos por extenso (ex: 'número um', 'número dois', 'primeiro', 'segundo').\n"
        "   - Números por Extenso: Absolutamente TODOS os números, datas, horários, valores monetários e documentos devem ser escritos por extenso (ex: 'cinco', 'vinte e nove', 'dez horas', 'dois mil e vinte e seis'). Não use numerais cardinais ou ordinais.\n"
        "   - Verbos no Passado: Todos os acontecimentos e discussões devem ser relatados no pretérito perfeito do indicativo (ex: 'reuniram-se', 'deliberou-se', 'aprovou-se', 'declarou').\n"
        "   - Sem rasuras: Caso detecte contradições ou correções no markdown de origem, utilize a palavra 'digo' para efetuar a correção na hora (ex: 'Aos vinte dias, digo, vinte e nove dias do mês de maio...').\n"
    )
    
    prompt_usuario = (
        f"JSON Schema de Contrato:\n{json.dumps(schema_content, indent=2)}\n\n"
        f"Ata em Markdown a ser convertida:\n{markdown_content}"
    )
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    print("Enviando solicitação de estruturação ao Groq (Llama 3.3 70B)...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Erro na API do Groq: Status {response.status_code}")
            print(response.text)
            sys.exit(1)
            
        resposta_json = response.json()
        conteudo_retornado = resposta_json["choices"][0]["message"]["content"]
        return json.loads(conteudo_retornado.strip())
    except Exception as e:
        print(f"Erro ao comunicar com a API do Groq: {e}")
        sys.exit(1)

def validar_json(instancia_json, schema_json):
    """Valida o JSON contra o schema usando jsonschema."""
    try:
        from jsonschema import validate
        validate(instance=instancia_json, schema=schema_json)
        print("Validação bem-sucedida! O JSON segue o contrato do schema_ata.json.")
        return True
    except ImportError:
        print("Aviso: Biblioteca 'jsonschema' não instalada no ambiente virtual.")
        print("Realizando validação básica manual...")
        # Validação simples de campos obrigatórios caso o jsonschema não esteja disponível
        campos_obrigatorios = ["titulo", "data", "local", "participantes", "resumo_assuntos", "encaminhamentos", "duvidas_incertezas"]
        for campo in campos_obrigatorios:
            if campo not in instancia_json:
                print(f"Erro de validação manual: Campo obrigatório '{campo}' está ausente.")
                return False
        print("Validação manual básica passou com sucesso.")
        return True
    except Exception as e:
        print(f"Erro de Validação de Contrato (JSON Schema): {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Converte uma ata em Markdown para JSON estruturado e realiza a validação do contrato de dados."
    )
    parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo Markdown de ata simplificada.")
    parser.add_argument("-s", "--schema", default="schemas/schema_ata.json", help="Caminho para o arquivo JSON Schema.")
    parser.add_argument("-o", "--output", help="Caminho do arquivo JSON de saída (padrão: mesma pasta da ata de entrada).")
    parser.add_argument("-k", "--key", help="Chave da API do Groq.")
    
    args = parser.parse_args()
    
    # 1. Carrega a chave de API
    api_key = obter_api_key(args)
    
    # 2. Verifica caminhos de entrada
    if not os.path.exists(args.input):
        print(f"Erro: Arquivo de entrada '{args.input}' não encontrado.")
        sys.exit(1)
        
    if not os.path.exists(args.schema):
        print(f"Erro: Arquivo do JSON Schema '{args.schema}' não encontrado.")
        sys.exit(1)
        
    # 3. Lê o Markdown e o Schema
    with open(args.input, "r", encoding="utf-8") as f:
        markdown_content = f.read()
        
    with open(args.schema, "r", encoding="utf-8") as f:
        schema_content = json.load(f)
        
    # 4. Envia ao Groq para gerar o JSON
    dados_estruturados = estruturar_com_groq(markdown_content, schema_content, api_key)
    
    # 5. Realiza a validação contratual
    valido = validar_json(dados_estruturados, schema_content)
    
    if not valido:
        print("Erro: O JSON gerado não atende aos critérios do contrato (JSON Schema).")
        sys.exit(1)
        
    # 6. Salva o resultado
    output_path = args.output
    if not output_path:
        output_path = os.path.splitext(args.input)[0].replace("_simplificada", "") + ".json"
        # Garante que o nome do arquivo seja ata.json se o arquivo base for ata_simplificada.md
        if output_path.endswith("ata.json") or output_path.endswith("ata_simplificada.json"):
            output_path = os.path.join(os.path.dirname(args.input), "ata.json")
            
    # Garante diretório de saída
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dados_estruturados, f, indent=2, ensure_ascii=False)
        
    print(f"Sucesso! Ata estruturada salva em '{output_path}'.")

if __name__ == "__main__":
    main()
