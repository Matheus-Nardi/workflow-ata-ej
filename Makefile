# Makefile para automatizar a transcrição de áudio das reuniões

# Configurações de variáveis (podem ser sobrescritas ao chamar o comando)
PASTA ?=
AUDIO ?= audio.mp3
INPUT = $(PASTA)/$(AUDIO)
OUTPUT = $(PASTA)/transcricao.txt

VENV = .venv
PYTHON = $(VENV)/bin/python

.PHONY: ajuda transcrever

ajuda:
	@echo "=== Utilitário de Transcrição de Reuniões ==="
	@echo "Uso:"
	@echo "  make transcrever PASTA=<caminho_da_pasta> [AUDIO=<nome_do_audio>]"
	@echo ""
	@echo "Argumentos:"
	@echo "  PASTA    Caminho da pasta da reunião (Obrigatório)"
	@echo "  AUDIO    Nome do arquivo de áudio dentro da pasta (Padrão: audio.mp3)"
	@echo ""
	@echo "Exemplo:"
	@echo "  make transcrever PASTA=reunioes/reuniao_2026-06-04"
	@echo "  make transcrever PASTA=reunioes/reuniao_2026-06-04 AUDIO=gravacao.m4a"

transcrever:
	@if [ -z "$(PASTA)" ]; then \
		echo "Erro: Você deve especificar o parâmetro PASTA."; \
		echo "Exemplo: make transcrever PASTA=reunioes/reuniao_2026-06-04"; \
		exit 1; \
	fi
	@if [ ! -f "$(INPUT)" ]; then \
		echo "Erro: Arquivo de áudio '$(INPUT)' não encontrado."; \
		exit 1; \
	fi
	@echo "Iniciando transcrição de '$(INPUT)'..."
	@$(PYTHON) scripts/transcrever.py -i "$(INPUT)" -o "$(OUTPUT)"
