#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
import subprocess
from pathlib import Path

# 配置
BASE_DIR = Path(__file__).parent.absolute()  # 使用當前腳本所在目錄
QUESTIONS_DIR = BASE_DIR / 'normalized_questions'
OUTPUT_DIR = BASE_DIR / 'anki_output'
MARKDOWN_DIR = BASE_DIR / 'markdown_input'
MEDIA_DIR = MARKDOWN_DIR / 'media'

# 確保輸出目錄存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MARKDOWN_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)

def copy_image_files(src_dir, dest_dir, question_num):
    """複製圖片文件到媒體目錄"""
    images = []
    if not os.path.exists(src_dir):
        return images
    
    for file in os.listdir(src_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
            src_path = os.path.join(src_dir, file)
            # 創建一個唯一的文件名，包含問題編號
            new_filename = f"q{question_num:03d}_{file}"
            dest_path = os.path.join(dest_dir, new_filename)
            shutil.copy2(src_path, dest_path)
            images.append((file, f"media/{new_filename}"))
    
    return images

def sanitize_markdown(text):
    """處理文本中可能干擾Markdown結構的標記"""
    # 將 ## 替換為 * 以避免干擾 Markdown 結構
    return text.replace('##', '*')

def generate_markdown():
    """生成適用於md2anki的Markdown文件"""
    question_nums = list(range(1, 121))
    processed_count = 0
    
    markdown_path = MARKDOWN_DIR / 'anki_deck.md'
    
    with open(markdown_path, 'w', encoding='utf-8') as md_file:
        # 寫入標題
        md_file.write("# 腫專2024\n\n")
        
        for question_num in question_nums:
            question_dir = QUESTIONS_DIR / f"{question_num:03d}"
            
            # 檢查問題目錄是否存在
            if not os.path.exists(question_dir):
                nested_dir = question_dir / f"{question_num:03d}"
                if os.path.exists(nested_dir):
                    question_dir = nested_dir
                else:
                    print(f"警告: 找不到問題 {question_num:03d} 的目錄")
                    continue
            
            # 讀取問題文件
            question_file = question_dir / "question.txt"
            if not os.path.exists(question_file):
                print(f"警告: 找不到問題 {question_num:03d} 的問題文件")
                continue
            
            with open(question_file, 'r', encoding='utf-8') as f:
                question_text = f.read().strip()
            
            # 讀取選項
            option_files = {
                'A': question_dir / "option_A.txt",
                'B': question_dir / "option_B.txt",
                'C': question_dir / "option_C.txt",
                'D': question_dir / "option_D.txt",
                'E': question_dir / "option_E.txt"
            }
            
            options = {}
            for option, file_path in option_files.items():
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        options[option] = f.read().strip()
                else:
                    options[option] = ""
            
            # 讀取正確答案
            correct_answer_file = question_dir / "correct_answer.txt"
            if os.path.exists(correct_answer_file):
                with open(correct_answer_file, 'r', encoding='utf-8') as f:
                    correct_answer = f.read().strip()
            else:
                correct_answer = "未提供"
            
            # 讀取解釋
            explanation_file = question_dir / "explain.txt"
            if os.path.exists(explanation_file):
                with open(explanation_file, 'r', encoding='utf-8') as f:
                    explanation = f.read().strip()
            else:
                explanation = "未提供解釋"
            
            # 複製圖片文件
            question_images = copy_image_files(question_dir / "question_figures", MEDIA_DIR, question_num)
            explain_images = copy_image_files(question_dir / "explain_figures", MEDIA_DIR, question_num)
            
            # 寫入問題標題
            md_file.write(f"## Question {question_num:03d}\n\n")
            
            # 前面部分（問題和選項）
            front_content = f"{question_text}\n\n"
            
            # 添加問題圖片
            for orig_name, new_name in question_images:
                front_content += f"![{orig_name}]({new_name})\n\n"
            
            # 添加選項
            front_content += "**選項：**\n\n"
            for option in ['A', 'B', 'C', 'D', 'E']:
                if options.get(option):
                    front_content += f"**{option}.** {options[option]}\n\n"
            
            # 寫入前面部分
            md_file.write(front_content)
            
            # 分隔前後面
            md_file.write("---\n\n")
            
            # 後面部分（答案和解釋）
            back_content = f"**正確答案：{correct_answer}**\n\n"
            back_content += "**解釋：**\n\n"
            
            # 處理解釋文字，將 ## 替換為 * 以避免干擾 Markdown 結構
            for line in explanation.split('\n'):
                if line.strip():
                    # 處理可能干擾Markdown結構的標記
                    sanitized_line = sanitize_markdown(line)
                    back_content += f"{sanitized_line}\n\n"
            
            # 添加解釋圖片
            for orig_name, new_name in explain_images:
                back_content += f"![{orig_name}]({new_name})\n\n"
            
            # 寫入後面部分
            md_file.write(back_content)
            
            # 分隔不同卡片
            md_file.write("---\n\n")
            
            processed_count += 1
    
    print(f"Markdown 檔案已生成: {markdown_path}")
    print(f"成功處理了 {processed_count} 個問題")
    return markdown_path

def generate_anki_deck(markdown_path):
    """使用md2anki生成Anki牌組"""
    print("開始生成 Anki 牌組...")
    
    # 確保輸出目錄存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 設置輸出文件路徑
    output_apkg = OUTPUT_DIR / "anki_deck.apkg"
    
    # 構建md2anki命令
    cmd = [
        "md2anki",
        str(markdown_path),
        "-o-anki", str(output_apkg),
        "-file-dir", str(MARKDOWN_DIR)
    ]
    
    # 執行命令
    try:
        subprocess.run(cmd, check=True)
        print("成功生成 Anki 牌組!")
        print(f"Anki 牌組位於: {OUTPUT_DIR}")
    except subprocess.CalledProcessError as e:
        print(f"生成 Anki 牌組時出錯: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # 生成Markdown文件
    markdown_path = generate_markdown()
    
    # 生成Anki牌組
    if generate_anki_deck(markdown_path):
        print(f"完成! Anki 牌組已生成，包含所有問題")
    else:
        print("生成 Anki 牌組失敗")
