# Guia da Fase 3 - Integração GitHub MCP e Otimização

Esta fase adiciona integração de dados externos ao workflow de atas de reunião, permitindo à inteligência artificial ler o status recente de desenvolvimento diretamente dos repositórios do GitHub da organização através do protocolo **MCP (Model Context Protocol)** e exibi-los em uma seção especial na ata.

## Objetivos da Fase 3
1. **Contextualização com Ferramentas (MCP):** Habilitar a IA a buscar informações como últimos commits e atividades do GitHub em tempo real antes de escrever a ata.
2. **Estrutura de Dados Ampliada:** Atualizar o contrato de dados JSON para suportar a propriedade opcional `status_desenvolvimento`.
3. **Renderização Dinâmica no Word:** Atualizar o script de Word para injetar dinamicamente a tabela corporativa de status ao final do documento, se presente.
4. **Resiliência a Falhas (Fallback):** Garantir que o workflow prossiga normalmente mesmo se a busca no GitHub falhar ou se o usuário optar por não integrá-la.

---

## Como Funciona a Integração MCP
O **Model Context Protocol (MCP)** permite que a IA conecte-se a serviços externos. Durante a Fase 1 (sumarização), se o usuário solicitar o status do desenvolvimento ou se houver menção aos repositórios da EJ:
1. O agente utiliza a ferramenta do MCP GitHub configurada no Antigravity.
2. A ferramenta lê o repositório em nome de uma conta com acesso de leitura (sua conta pessoal ou um bot/membro convidado).
3. A IA compila e adiciona a seção `Status de Desenvolvimento` na ata simplificada em Markdown (`ata_simplificada.md`).

---

## Validação de Contrato (JSON Schema)
O campo `status_desenvolvimento` no JSON segue a seguinte especificação técnica opcional:
```json
"status_desenvolvimento": {
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "repositorio": { "type": "string" },
      "commits_recentes": { "type": ["integer", "string"] },
      "ultimo_commit": { "type": "string" },
      "data": { "type": "string" }
    },
    "required": ["repositorio"],
    "additionalProperties": false
  }
}
```

---

## Critérios de Aceite e Testes

### 1. Teste de Validação Local (Sem erro em atas antigas)
Atas das fases anteriores (que não possuem dados de GitHub) devem continuar passando na validação e gerando o Word normalmente, pois a propriedade é opcional.

### 2. Renderização de Elementos no Docx
Se o JSON contiver `status_desenvolvimento`, a tabela correspondente é criada ao final do Word seguindo a identidade TechTins (cabeçalho roxo, fonte Times New Roman, linhas zebradas e alinhamento centralizado).
