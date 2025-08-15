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
MARKDOWN_DIR = $(BASE_DIR)/anki_markdown_decks
MDBOOK_DIR = $(BASE_DIR)/mdbook
MKDOC_DIR = $(BASE_DIR)/mkdoc

# 腳本
EXTRACT_SCRIPT = $(BASE_DIR)/extract_and_normalize.py
DECK_SCRIPT = $(BASE_DIR)/convert_to_mdankideck.py
MDBOOK_SCRIPT = $(BASE_DIR)/create_mdbook.py
MKDOC_SCRIPT = $(BASE_DIR)/to_mkdoc.py
SHEET_SCRIPT = $(BASE_DIR)/to_sheets.py

# 默認目標
.PHONY: all
all: env extract deck mdbook mkdoc

# 創建虛擬環境並安裝依賴
.PHONY: env
env:
	@echo "創建虛擬環境並安裝依賴..."
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	@$(VENV_ACTIVATE) && $(PIP) install markdown-anki-decks pandas openpyxl
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

# 生成mdBook
.PHONY: mdbook
mdbook:
	@echo "生成mdBook..."
	@$(VENV_ACTIVATE) && $(PYTHON) $(MDBOOK_SCRIPT)
	@echo "mdBook生成完成"

# 生成mkdoc
.PHONY: mkdoc
mkdoc:
	@echo "生成mkdoc..."
	@$(VENV_ACTIVATE) && $(PYTHON) $(MKDOC_SCRIPT)
	@echo "mkdoc生成完成"

# 生成Excel表格
.PHONY: sheet
sheet:
	@echo "生成Excel表格..."
	@$(VENV_ACTIVATE) && $(PYTHON) $(SHEET_SCRIPT)
	@echo "Excel表格生成完成"

# 清理生成的文件
.PHONY: clean
clean:
	@echo "清理生成的文件..."
	@rm -rf $(OUTPUT_DIR)/* $(MARKDOWN_DIR)/* $(MDBOOK_DIR)/* $(MKDOC_DIR)/*
	@rm -f questions_sheet.xlsx medical_questions.apkg
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
	@echo "  make mdbook   - 生成mdBook"
	@echo "  make mkdoc    - 生成mkdoc"
	@echo "  make sheet    - 生成Excel表格"
	@echo "  make clean    - 清理生成的文件"
	@echo "  make clean-all - 完全清理（包括虛擬環境）"
	@echo "  make all      - 執行所有步驟（env, extract, deck, mdbook, mkdoc）"
	@echo "  make help     - 顯示此幫助信息"