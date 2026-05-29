# Product Requirements Document (PRD) - Workflow Gerador de Atas

## 1. Visão Geral e Objetivos

**Problema:**
A Empresa Júnior de Sistemas de Informação realiza reuniões periodicamente. A criação das atas dessas reuniões é um processo manual, onde um responsável precisa ouvir o áudio e elencar os principais pontos. Tentativas anteriores com IAs simples falharam devido à dificuldade de compreensão de certas falas e na identificação correta dos assuntos discutidos.

**Solução:**
Desenvolver um workflow automatizado no Antigravity, acionado pelo comando `/gerar-ata`, capaz de receber o áudio de uma reunião e o nome dos participantes para transcrição, sumarização e formatação automática de uma ata de reunião. 

**Público-Alvo:**
- Membros e Diretoria da Empresa Júnior.
- Avaliador(a) (Professor) da disciplina de Inteligência Artificial.

**Objetivos do Projeto:**
1. Criar um workflow de automação para atas de reunião.
2. Gerar uma ata padronizada (com encaminhamentos, destaques de pontos relevantes e próximos passos) e aderente ao template visual da empresa (banner/rodapé).
3. Desenvolver uma integração (opcional) com o GitHub da organização para incluir relatórios de progresso via protocolo MCP.
4. Entregar um projeto prático, versionado, estruturado e útil para a disciplina de IA.

---

## 2. Requisitos e Escopo (Desenvolvimento em Fases)

O projeto será desenvolvido iterativamente, dividido em três fases principais para garantir entregas e validações contínuas.

### Fase 1: MVP (Transcrição e Sumarização Básica)
**Objetivo:** Validar a capacidade de interpretação do modelo de linguagem a partir do áudio e gerar um resumo estruturado e coerente.

*   **Critérios de Inclusão:**
    *   Comando base `/gerar-ata`.
    *   Recebimento do áudio e da lista de participantes via prompt/chat.
    *   Transcrição do áudio e extração de tópicos principais.
*   **Critérios de Exclusão (Fora de Escopo):**
    *   Formatação final no template da Empresa Júnior.
    *   Integração com GitHub.
*   **Demonstração Mínima:**
    *   O usuário envia o áudio de uma reunião teste e a IA retorna um texto legível identificando quem participou e quais foram os pontos discutidos de forma clara.
*   **Critérios de Aceite:**
    *   A IA deve conseguir superar as falhas das tentativas anteriores, interpretando as falas com precisão aceitável (mínimo de alucinações e distorções de contexto).
    *   O consumo de tokens deve ser monitorado e documentado.

### Fase 2: Estruturação, Template e Formatação
**Objetivo:** Transformar o resumo gerado na Fase 1 em um documento final pronto para uso institucional, preenchendo o template oficial da Empresa Júnior.

*   **Critérios de Inclusão:**
    *   Uso de um arquivo base em formato **.docx** contendo o layout padrão da EJ (cabeçalho, banner, rodapé e formatação institucional).
    *   Inserção dinâmica de dados na ata (Participantes, Assuntos Discutidos, Encaminhamentos, Próximos Passos) dentro do template `.docx`.
    *   Exportação do documento final também em formato **.docx**.
*   **Critérios de Exclusão:**
    *   Integrações externas além do LLM.
*   **Demonstração Mínima:**
    *   Ao executar o comando, o Antigravity gera um arquivo `.docx` populado que, ao ser aberto, segue rigorosamente a identidade visual e o design padrão da EJ.
*   **Critérios de Aceite:**
    *   A formatação original do arquivo base `.docx` (fontes, margens, banners) deve ser perfeitamente preservada após a inserção dos textos da ata.
    *   O documento gerado deve conter todas as seções obrigatórias especificadas.

### Fase 3: Integração GitHub (MCP) e Otimização
**Objetivo:** Adicionar inteligência externa ao workflow para enriquecer a ata com dados de desenvolvimento da equipe.

*   **Critérios de Inclusão:**
    *   Parâmetro opcional no comando para incluir dados do GitHub.
    *   Comunicação via MCP para buscar status de repositórios, commits recentes e atividade dos participantes da organização.
    *   Estratégias de otimização de tokens (ex: refinamento do prompt, pré-processamento do áudio se necessário).
*   **Critérios de Exclusão:**
    *   Modificações ou operações de escrita nos repositórios do GitHub (apenas leitura de dados).
*   **Demonstração Mínima:**
    *   A ata gerada inclui uma seção extra: "Status de Desenvolvimento", populada com dados reais do GitHub da organização no período analisado.
*   **Critérios de Aceite:**
    *   A chamada MCP deve ocorrer sem erros e integrar os dados de forma coesa com o texto da ata.
    *   O workflow deve continuar funcionando normalmente (fallback) caso o usuário opte por não incluir os dados do GitHub ou a requisição falhe.

### Fase 4: Conversão para PDF (Opcional) e Notificação por E-mail
**Objetivo:** Automatizar a distribuição da ata finalizada para toda a equipe em formato PDF (ou DOCX como fallback).

*   **Critérios de Inclusão:**
    *   Conversão do documento oficial do formato `.docx` para `.pdf` utilizando o LibreOffice Headless (opcional).
    *   Envio automático de e-mail SMTP para todos os membros cadastrados na base do sistema (`config/membros.json`).
    *   Anexo da ata convertida em formato PDF (ou o arquivo `.docx` original caso o LibreOffice não esteja instalado).
    *   Disparo seguro de credenciais a partir de variáveis de ambiente (`.env`).
*   **Demonstração Mínima:**
    *   Após a validação e geração da ata em Word, o workflow gera o arquivo PDF no mesmo diretório (ou usa o `.docx` se o conversor não estiver instalado) e todos os membros cadastrados recebem a mensagem do bot com o documento anexado.
*   **Critérios de Aceite:**
    *   Se o LibreOffice estiver instalado, o documento PDF gerado deve ser idêntico visualmente ao `.docx`.
    *   O e-mail deve ser entregue com sucesso aos destinatários válidos contendo a ata anexada (seja em PDF ou DOCX).
    *   O assunto e corpo do e-mail devem ser profissionais e objetivos.

---

## 3. Fluxo do Usuário (User Flow)

1.  O usuário abre o chat do Antigravity.
2.  Digita o comando `/gerar-ata` anexando o arquivo de áudio da reunião, fornecendo a lista de participantes e passando opcionalmente metadados no prompt (ex: título/pauta da reunião, data, local e horário) bem como o parâmetro para inclusão do GitHub.
3.  O agente de IA recebe e processa o áudio (transcrição).
4.  O agente (se solicitado) faz a requisição MCP para o GitHub da organização.
5.  O agente formata os dados transcritos juntamente com os dados do Github, aplicando o template da Empresa Júnior.
6.  O agente gera a ata em formato Word (`ata.docx`).
7.  O agente converte a ata para PDF (`ata.pdf`) e distribui automaticamente para todos os membros cadastrados no sistema via e-mail.
8.  O agente confirma a conclusão de todo o processo e retorna o status do envio.

---

## 4. Requisitos Não Funcionais e Decisões Arquiteturais

-   **Qualidade da Transcrição:** É fundamental escolher um modelo capaz de entender o contexto da área de tecnologia, gírias ou termos técnicos usados na EJ.
-   **Custo Zero (Ferramenta Gratuita):** O projeto deve operar sem gerar custos financeiros recorrentes para a Empresa Júnior. 
    *   *Decisão de Arquitetura:* A transcrição pesada do áudio será delegada para a **API da Groq (modelo Whisper Large)**. Esta abordagem foi escolhida por entregar altíssima velocidade e precisão no idioma português, operando inteiramente dentro do plano gratuito (free tier) da plataforma, que atende com folga ao volume e tamanho (até 100MB/arquivo) das atas da EJ.
-   **Volume de Dados / Duração:** As reuniões duram tipicamente de **30 a 40 minutos**. Isso garante que o tamanho do arquivo de áudio compactado (ex: MP3) fique bem abaixo do limite de 100 MB da API da Groq e que o volume de texto gerado caiba facilmente na janela de contexto de modelos de sumarização (como o Gemini 1.5 Flash ou Pro), evitando a necessidade de fatiamento complexo de texto.
-   **Distribuição e Deploy Local:** O workflow será configurado inicialmente para execução de forma **local no ambiente do desenvolvedor**. O código e as instruções de instalação do Antigravity serão versionados em um repositório Git, permitindo que outros colegas clonem e utilizem localmente no futuro caso queiram, sem necessidade de um servidor centralizado ou infraestrutura de deploy complexa.
-   **Otimização de Custos/Tokens:** Como áudios de reuniões podem ser extensos, o modelo de sumarização no Antigravity deve ser configurado de maneira a evitar desperdício de tokens de contexto.
-   **Versionamento:** O workflow e seus artefatos (incluindo este PRD) devem ser mantidos versionados em um repositório GitHub para viabilizar colaboração (conforme modelo sugerido pelo professor).
