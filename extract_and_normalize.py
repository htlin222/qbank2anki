#!/usr/bin/env python3
"""
模組用於解壓縮和標準化 zips 目錄中的所有壓縮檔
確保所有問題資料夾都有正確的結構和檔案名稱
"""

import os
import shutil
import zipfile
import re
import glob
import subprocess
from pathlib import Path

# 配置路徑
BASE_DIR = "/Users/htlin/Downloads/校稿完成"
ZIPS_DIR = os.path.join(BASE_DIR, "zips")
EXTRACT_DIR = os.path.join(BASE_DIR, "normalized_questions")

# 確保輸出目錄存在
os.makedirs(EXTRACT_DIR, exist_ok=True)

def extract_zip_file(zip_path, extract_to):
    """解壓縮 ZIP 或 RAR 檔案到指定目錄"""
    if zip_path.endswith('.zip'):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        except Exception as e:
            print(f"解壓縮 ZIP 檔案 {zip_path} 時出錯: {e}")
            return False
    elif zip_path.endswith('.rar'):
        try:
            # 使用 unar 命令解壓縮 RAR 檔案
            result = subprocess.run(['unar', '-d', '-o', extract_to, zip_path], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                print(f"成功使用 unar 解壓縮 {zip_path}")
                return True
            else:
                print(f"使用 unar 解壓縮 {zip_path} 時出錯: {result.stderr}")
                return False
        except Exception as e:
            print(f"執行 unar 命令時出錯: {e}")
            return False
    return False

def normalize_folder_structure(temp_dir, question_num):
    """標準化資料夾結構，確保所有必要的檔案都在正確的位置"""
    question_dir = f"{question_num:03d}"
    target_dir = os.path.join(EXTRACT_DIR, question_dir)
    
    # 如果目標目錄已存在，先刪除它
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    # 創建目標目錄
    os.makedirs(target_dir, exist_ok=True)
    
    # 檢查是否有嵌套的資料夾結構
    nested_dir = None
    
    # 尋找包含 question.txt 的資料夾
    for root, dirs, files in os.walk(temp_dir):
        if "question.txt" in files:
            nested_dir = root
            break
    
    if nested_dir:
        # 找到包含問題檔案的資料夾，將其內容複製到標準化目錄
        for item in os.listdir(nested_dir):
            src = os.path.join(nested_dir, item)
            dst = os.path.join(target_dir, item)
            
            if os.path.isdir(src):
                # 確保圖片資料夾存在
                if item in ["question_figures", "explain_figures"]:
                    os.makedirs(dst, exist_ok=True)
                    for img in os.listdir(src):
                        img_src = os.path.join(src, img)
                        img_dst = os.path.join(dst, img)
                        if os.path.isfile(img_src):
                            shutil.copy2(img_src, img_dst)
                else:
                    # 其他資料夾，可能是嵌套結構
                    for sub_item in os.listdir(src):
                        sub_src = os.path.join(src, sub_item)
                        if os.path.isdir(sub_src) and sub_item in ["question_figures", "explain_figures"]:
                            sub_dst = os.path.join(target_dir, sub_item)
                            os.makedirs(sub_dst, exist_ok=True)
                            for img in os.listdir(sub_src):
                                img_src = os.path.join(sub_src, img)
                                img_dst = os.path.join(sub_dst, img)
                                if os.path.isfile(img_src):
                                    shutil.copy2(img_src, img_dst)
            elif os.path.isfile(src):
                # 複製檔案
                shutil.copy2(src, dst)
    else:
        # 沒有找到包含問題檔案的資料夾，嘗試直接複製所有檔案
        print(f"警告: 在 {temp_dir} 中找不到 question.txt，嘗試直接複製所有檔案")
        for item in os.listdir(temp_dir):
            src = os.path.join(temp_dir, item)
            dst = os.path.join(target_dir, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif os.path.isfile(src):
                shutil.copy2(src, dst)
    
    # 確保所有必要的檔案和資料夾都存在
    ensure_required_files(target_dir)
    
    return target_dir

def ensure_required_files(dir_path):
    """確保所有必要的檔案和資料夾都存在"""
    # 確保圖片資料夾存在
    os.makedirs(os.path.join(dir_path, "question_figures"), exist_ok=True)
    os.makedirs(os.path.join(dir_path, "explain_figures"), exist_ok=True)
    
    # 檢查必要的文字檔案
    required_files = [
        "question.txt",
        "option_A.txt",
        "option_B.txt",
        "option_C.txt",
        "option_D.txt",
        "option_E.txt",
        "correct_answer.txt",
        "explain.txt"
    ]
    
    for file in required_files:
        file_path = os.path.join(dir_path, file)
        if not os.path.exists(file_path):
            # 如果檔案不存在，創建一個空檔案
            with open(file_path, 'w', encoding='utf-8') as f:
                if file == "correct_answer.txt":
                    f.write("?")  # 預設答案為問號
                else:
                    f.write("")  # 其他檔案為空

def process_zip_files():
    """處理 zips 目錄中的所有壓縮檔"""
    # 獲取所有 zip 檔案
    zip_files = []
    for ext in ['*.zip', '*.rar']:
        zip_files.extend(glob.glob(os.path.join(ZIPS_DIR, ext)))
    
    zip_files.sort()
    
    # 用於跟踪已處理的問題編號
    processed_questions = set()
    
    # 處理每個壓縮檔
    for zip_file in zip_files:
        # 從檔案名稱中提取問題編號
        filename = os.path.basename(zip_file)
        match = re.match(r'(\d+)\.(?:zip|rar)', filename)
        if match:
            question_num = int(match.group(1))
            
            # 如果這個問題已經處理過，跳過
            if question_num in processed_questions:
                print(f"跳過已處理的問題 {question_num:03d}")
                continue
            
            print(f"處理問題 {question_num:03d} 從 {filename}")
            
            # 創建臨時目錄用於解壓縮
            temp_dir = os.path.join(EXTRACT_DIR, f"temp_{question_num:03d}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
            
            # 解壓縮檔案 (ZIP 或 RAR)
            if extract_zip_file(zip_file, temp_dir):
                # 標準化資料夾結構
                normalize_folder_structure(temp_dir, question_num)
                processed_questions.add(question_num)
            else:
                # 如果解壓縮失敗，嘗試從主目錄複製
                print(f"嘗試從主目錄複製問題 {question_num:03d}")
                source_dir = os.path.join(BASE_DIR, f"{question_num:03d}")
                if os.path.exists(source_dir) and os.path.isdir(source_dir):
                    normalize_folder_structure(source_dir, question_num)
                    processed_questions.add(question_num)
                else:
                    print(f"錯誤: 找不到問題 {question_num:03d} 的資料夾")
            
            # 清理臨時目錄
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    # 處理主目錄中的問題資料夾
    for i in range(1, 121):
        if i not in processed_questions:
            question_dir = f"{i:03d}"
            source_dir = os.path.join(BASE_DIR, question_dir)
            if os.path.exists(source_dir) and os.path.isdir(source_dir):
                print(f"從主目錄處理問題 {i:03d}")
                normalize_folder_structure(source_dir, i)
                processed_questions.add(i)
    
    # 檢查是否所有 120 個問題都已處理
    missing_questions = []
    for i in range(1, 121):
        if i not in processed_questions:
            missing_questions.append(i)
    
    if missing_questions:
        print(f"警告: 以下問題未處理: {missing_questions}")
    else:
        print("成功: 所有 120 個問題都已處理")
    
    return len(processed_questions)

def main():
    """主函數"""
    print("開始處理壓縮檔案並標準化問題資料夾結構...")
    num_processed = process_zip_files()
    print(f"完成! 共處理了 {num_processed} 個問題")
    print(f"標準化的問題資料夾位於: {EXTRACT_DIR}")

if __name__ == "__main__":
    main()
