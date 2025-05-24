# Anki牌組生成Makefile

# 配置
PYTHON = python
VENV = .venv
VENV_ACTIVATE = source $(VENV)/bin/activate
UV = uv
PIP = $(UV) pip

# 目錄
BASE_DIR = .
ZIPS_DIR = $(BASE_DIR)/zips
NORMALIZED_DIR = $(BASE_DIR)/normalized_questions
OUTPUT_DIR = $(BASE_DIR)/anki_output
MARKDOWN_DIR = $(BASE_DIR)/markdown_input

# 腳本
EXTRACT_SCRIPT = $(BASE_DIR)/extract_and_normalize.py
DECK_SCRIPT = $(BASE_DIR)/generate_anki_with_md2anki.py

# 默認目標
.PHONY: all
all: env extract deck

# 創建虛擬環境並安裝依賴
.PHONY: env
env:
	@echo "創建虛擬環境並安裝依賴..."
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	@$(VENV_ACTIVATE) && $(PIP) install md2anki
	@echo "虛擬環境設置完成"

# 提取和標準化問題文件夾
.PHONY: extract
extract:
	@echo "提取和標準化問題文件夾..."
	@$(VENV_ACTIVATE) && $(PYTHON) $(EXTRACT_SCRIPT)
	@echo "提取和標準化完成"

# 生成Anki牌組
.PHONY: deck
deck:
	@echo "生成Anki牌組..."
	@$(VENV_ACTIVATE) && $(PYTHON) $(DECK_SCRIPT)
	@echo "Anki牌組生成完成"

# 清理生成的文件
.PHONY: clean
clean:
	@echo "清理生成的文件..."
	@rm -rf $(OUTPUT_DIR)/* $(MARKDOWN_DIR)/*
	@echo "清理完成"

# 完全清理（包括虛擬環境）
.PHONY: clean-all
clean-all: clean
	@echo "清理虛擬環境..."
	@rm -rf $(VENV)
	@echo "完全清理完成"

# 幫助信息
.PHONY: help
help:
	@echo "可用命令:"
	@echo "  make env      - 創建虛擬環境並安裝依賴"
	@echo "  make extract  - 提取和標準化問題文件夾"
	@echo "  make deck     - 生成Anki牌組"
	@echo "  make clean    - 清理生成的文件"
	@echo "  make clean-all - 完全清理（包括虛擬環境）"
	@echo "  make all      - 執行所有步驟（env, extract, deck）"
	@echo "  make help     - 顯示此幫助信息"
