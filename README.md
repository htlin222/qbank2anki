# 腫專2024 Anki牌組生成工具

這個工具用於從標準化的問題文件夾生成Anki牌組，適用於腫專2024的考試準備。

## 目錄結構

- `zips/` - 原始壓縮文件目錄
- `normalized_questions/` - 標準化後的問題文件夾
- `markdown_input/` - 生成的Markdown文件和媒體文件
- `anki_output/` - 最終生成的Anki牌組
- `tmp/` - 臨時文件目錄

## 使用方法

本項目使用Makefile來簡化工作流程，所有命令都可以通過make來執行。

### 設置環境

```bash
make env
```

這將創建一個虛擬環境並使用uv安裝所需的依賴項（md2anki）。

### 提取和標準化問題文件夾

```bash
make extract
```

這將從zips目錄中提取壓縮文件，並將問題文件夾標準化到normalized_questions目錄。

### 生成Anki牌組

```bash
make deck
```

這將從標準化的問題文件夾生成Anki牌組，輸出到anki_output目錄。

### 一次執行所有步驟

```bash
make all
```

這將按順序執行環境設置、提取和標準化、生成Anki牌組的所有步驟。

### 清理生成的文件

```bash
make clean
```

這將清理生成的輸出文件，但保留虛擬環境。

### 完全清理

```bash
make clean-all
```

這將清理所有生成的文件，包括虛擬環境。

## 文件說明

- `extract_and_normalize.py` - 提取和標準化問題文件夾的腳本
- `generate_anki_with_md2anki.py` - 生成Anki牌組的腳本
- `Makefile` - 自動化工作流程的配置文件

## 注意事項

- 腳本會自動處理問題文件中可能干擾Markdown結構的標記（如`##`）
- 生成的Anki牌組包含120個問題，每個問題的卡片前面都包含完整的問題內容和選項
- 所有圖片文件會被複製到markdown_input/media目錄，並在Anki牌組中正確顯示
