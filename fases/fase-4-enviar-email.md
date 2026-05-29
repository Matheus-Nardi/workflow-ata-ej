# Guia de Execução - Fase 4: Conversão para PDF e Envio por E-mail

Este documento descreve como configurar, executar e validar a distribuição automática de atas por e-mail em formato PDF.

---

## 1. Banco de Dados de Membros (`config/membros.json`)

Para que o script saiba para quem disparar os e-mails, mantemos um arquivo centralizado contendo o nome e o e-mail de todos os membros da Empresa Júnior.

Crie ou edite o arquivo `config/membros.json` seguindo o formato:
```json
{
  "Nome do Membro 1": "email1@exemplo.com",
  "Nome do Membro 2": "email2@exemplo.com"
}
```

*Nota: O script enviará a ata para **todos** os e-mails listados neste arquivo.*

---

## 2. Configurações de SMTP no `.env`

Para habilitar o disparo de e-mails reais, adicione as seguintes variáveis de ambiente no seu arquivo `.env` na raiz do projeto:

```env
SMTP_HOST=smtp.seuprovedor.com
SMTP_PORT=587
SMTP_USER=contato@suaempresa.com.br
SMTP_PASSWORD=sua_senha_de_aplicativo_aqui
```

### Como gerar a Senha de Aplicativo (Exemplo Gmail):
1. Acesse as configurações da sua Conta Google.
2. Vá em **Segurança** -> **Verificação em duas etapas** (deve estar ativa).
3. Role até o final da página e selecione **Senhas de app** (App Passwords).
4. Crie uma nova senha nomeando-a como "Orquestrador de Atas".
5. Copie a senha de 16 caracteres exibida e cole no campo `SMTP_PASSWORD` no `.env`.

---

## 3. Comandos de Execução

### Passo 1: Converter Word para PDF
Para converter a ata em formato `.docx` gerada na Fase 2 para `.pdf`, execute o script `converter_pdf.py` passando o arquivo de entrada:

```bash
.venv/bin/python3 scripts/converter_pdf.py -i reunioes/exemplo_2026-05-28/ata.docx
```

Isso criará o arquivo `reunioes/exemplo_2026-05-28/ata.pdf` na mesma pasta do arquivo original utilizando o LibreOffice de forma headless.

### Passo 2: Enviar E-mails aos Membros
Para realizar o envio dos e-mails aos membros cadastrados com a ata anexada, utilize o script `enviar_email.py`:

```bash
.venv/bin/python3 scripts/enviar_email.py -i reunioes/exemplo_2026-05-28/ata.pdf -t "Nome da Reunião"
```

#### Modo de Simulação (Dry-Run):
Para testar o envio sem fazer conexões reais com o SMTP do seu e-mail, adicione o parâmetro `--dry-run`:

```bash
.venv/bin/python3 scripts/enviar_email.py -i reunioes/exemplo_2026-05-28/ata.pdf -t "Alinhamento de Diretoria" --dry-run
```

*Nota: Caso as credenciais no `.env` estejam em branco ou com dados de exemplo (placeholders), o script automaticamente entra em modo de simulação (dry-run) para garantir a segurança da execução.*
