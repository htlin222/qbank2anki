#!/usr/bin/env python3
"""
Convert normalized_questions to mkdoc format
轉換 normalized_questions 到 mkdoc 格式
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class MkdocConverter:
    def __init__(self, source_dir: str = "normalized_questions", target_dir: str = "mkdoc"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
    def read_file_content(self, file_path: Path) -> str:
        """讀取文件內容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""
        except Exception as e:
            print(f"Warning: Error reading {file_path}: {e}")
            return ""
    
    def create_index_md(self, question_dir: Path) -> str:
        """生成 index.md 內容"""
        question_num = question_dir.name
        
        # 讀取各個文件
        question = self.read_file_content(question_dir / "question.txt")
        option_a = self.read_file_content(question_dir / "option_A.txt")
        option_b = self.read_file_content(question_dir / "option_B.txt")
        option_c = self.read_file_content(question_dir / "option_C.txt")
        option_d = self.read_file_content(question_dir / "option_D.txt")
        option_e = self.read_file_content(question_dir / "option_E.txt")
        correct_answer = self.read_file_content(question_dir / "correct_answer.txt")
        explain = self.read_file_content(question_dir / "explain.txt")
        
        # 構建 markdown 內容
        content = f"""# Question

## {question_num}

{question}



## Options

- [ ] **A**. {option_a}

- [ ] **B**. {option_b}

- [ ] **C**. {option_c}

- [ ] **D**. {option_d}

- [ ] **E**. {option_e}


## Correct Answer 

??? note
    {correct_answer}


## Explanation

{explain}
"""
        return content
    
    def create_note_md(self, question_dir: Path) -> str:
        """生成 note.md 內容 - 基本模板"""
        question_num = question_dir.name
        
        content = f"""# Note

## 考點🎯

### 待補充重點整理
- 本題考點需要進一步分析整理
- 相關概念和重要知識點
- 臨床應用和實務考量

## 重要概念
- 核心概念1
- 核心概念2
- 容易混淆的地方

## 快速複習要點
1. 重點1
2. 重點2
3. 重點3

"""
        return content
    
    def copy_figures(self, source_question_dir: Path, target_question_dir: Path):
        """複製圖片文件"""
        # 複製 question_figures
        source_q_fig = source_question_dir / "question_figures"
        target_figures = target_question_dir / "figures"
        
        if source_q_fig.exists() and any(source_q_fig.iterdir()):
            target_figures.mkdir(parents=True, exist_ok=True)
            for fig_file in source_q_fig.iterdir():
                if fig_file.is_file():
                    shutil.copy2(fig_file, target_figures / fig_file.name)
        
        # 複製 explain_figures
        source_e_fig = source_question_dir / "explain_figures"
        if source_e_fig.exists() and any(source_e_fig.iterdir()):
            target_figures.mkdir(parents=True, exist_ok=True)
            for fig_file in source_e_fig.iterdir():
                if fig_file.is_file():
                    shutil.copy2(fig_file, target_figures / fig_file.name)
    
    def convert_single_question(self, question_dir: Path):
        """轉換單個問題"""
        question_num = question_dir.name
        target_question_dir = self.target_dir / question_num
        
        # 創建目標目錄
        target_question_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成 index.md
        index_content = self.create_index_md(question_dir)
        with open(target_question_dir / "index.md", 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        # 生成 note.md (如果不存在的話)
        note_file = target_question_dir / "note.md"
        if not note_file.exists():
            note_content = self.create_note_md(question_dir)
            with open(note_file, 'w', encoding='utf-8') as f:
                f.write(note_content)
        
        # 複製圖片
        self.copy_figures(question_dir, target_question_dir)
        
        print(f"✓ Converted {question_num}")
    
    def convert_all(self):
        """轉換所有問題"""
        if not self.source_dir.exists():
            print(f"Error: Source directory {self.source_dir} does not exist")
            return
        
        # 創建目標目錄
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # 獲取所有問題目錄並排序
        question_dirs = [d for d in self.source_dir.iterdir() 
                        if d.is_dir() and d.name.isdigit()]
        question_dirs.sort(key=lambda x: int(x.name))
        
        print(f"Converting {len(question_dirs)} questions from {self.source_dir} to {self.target_dir}")
        
        for question_dir in question_dirs:
            try:
                self.convert_single_question(question_dir)
            except Exception as e:
                print(f"Error converting {question_dir.name}: {e}")
        
        print(f"\n✅ Conversion completed! {len(question_dirs)} questions converted.")

def main():
    converter = MkdocConverter()
    converter.convert_all()

if __name__ == "__main__":
    main()