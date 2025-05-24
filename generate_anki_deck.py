#!/usr/bin/env python3
import os
import shutil
import re
import html
import zipfile
import tempfile
from pathlib import Path
import glob
import sys

# Configuration
BASE_DIR = "/Users/htlin/Downloads/校稿完成"
ZIPS_DIR = os.path.join(BASE_DIR, "zips")
TEMP_DIR = os.path.join(BASE_DIR, "tmp")
EXTRACT_DIR = os.path.join(BASE_DIR, "extracted")
OUTPUT_MD_FILE = os.path.join(BASE_DIR, "anki_deck.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "anki_output")
CUSTOM_CSS_FILE = os.path.join(BASE_DIR, "custom.css")

# Create necessary directories if they don't exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

def read_file_content(file_path):
    """Read content from a file if it exists, otherwise return empty string."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return content
    return ""

def process_images(source_dir, question_num, prefix):
    """Copy images from source directory to temp directory with proper naming."""
    image_paths = []
    
    if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
        return image_paths
    
    for filename in os.listdir(source_dir):
        if filename.startswith('.'):  # Skip hidden files like .DS_Store
            continue
            
        # Get file extension
        _, ext = os.path.splitext(filename)
        if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
            continue
            
        # Create new filename
        new_filename = f"q{question_num:03d}_{prefix}_{filename}"
        new_path = os.path.join(TEMP_DIR, new_filename)
        
        # Copy file
        shutil.copy2(os.path.join(source_dir, filename), new_path)
        image_paths.append((filename, new_filename))
    
    return image_paths

def create_custom_css():
    """Create a custom CSS file for the Anki cards."""
    css_content = """
    .card {
        font-family: Arial, sans-serif;
        font-size: 16px;
        text-align: left;
        color: black;
        background-color: white;
        padding: 20px;
    }
    
    .question {
        margin-bottom: 15px;
    }
    
    .answer {
        margin-top: 15px;
    }
    
    .options {
        margin-left: 20px;
    }
    
    .correct-answer {
        font-weight: bold;
        color: #009900;
        margin: 10px 0;
    }
    
    .explanation {
        margin-top: 15px;
        border-top: 1px solid #ccc;
        padding-top: 15px;
    }
    
    img {
        max-width: 90%;
        height: auto;
        display: block;
        margin: 10px auto;
    }
    
    a {
        color: #0066cc;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    """
    
    with open(CUSTOM_CSS_FILE, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return CUSTOM_CSS_FILE

def extract_zip_file(zip_path, extract_to):
    """Extract a zip file to the specified directory."""
    if zip_path.endswith('.zip'):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        except Exception as e:
            print(f"Error extracting ZIP file {zip_path}: {e}")
            return False
    elif zip_path.endswith('.rar'):
        print(f"Warning: Cannot extract RAR file {zip_path} without additional tools.")
        print(f"Trying to find the question in the main directory instead.")
        return False
    return False

def find_question_files(question_num):
    """Find the actual directory containing question files.
    First check in the BASE_DIR, then try to extract from zips if not found.
    """
    question_dir = f"{question_num:03d}"
    base_path = os.path.join(BASE_DIR, question_dir)
    
    # Check if directory exists in BASE_DIR
    if os.path.isdir(base_path):
        # Check if this is a nested structure (folder contains a subfolder with the same name)
        nested_path = os.path.join(base_path, question_dir)
        if os.path.isdir(nested_path) and os.path.exists(os.path.join(nested_path, "question.txt")):
            return nested_path
        
        # Regular structure
        if os.path.exists(os.path.join(base_path, "question.txt")):
            return base_path
        
        # Try to find any subfolder that contains question.txt
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "question.txt")):
                return item_path
    
    # If not found in BASE_DIR, try to extract from zips
    extract_path = os.path.join(EXTRACT_DIR, question_dir)
    if not os.path.exists(extract_path):
        os.makedirs(extract_path, exist_ok=True)
        
        # Try different possible filenames (.zip, .rar, with/without leading zeros)
        possible_files = [
            os.path.join(ZIPS_DIR, f"{question_num:03d}.zip"),
            os.path.join(ZIPS_DIR, f"{question_num:d}.zip"),
        ]
        
        # First try ZIP files
        for zip_file in possible_files:
            if os.path.exists(zip_file):
                print(f"Extracting {zip_file} to {extract_path}")
                if extract_zip_file(zip_file, extract_path):
                    break
        
        # If ZIP extraction failed and the directory is still empty, try to copy from BASE_DIR
        if not os.listdir(extract_path):
            # For questions with RAR files, try to find the question in the main directory
            source_dir = os.path.join(BASE_DIR, question_dir)
            if os.path.exists(source_dir) and os.path.isdir(source_dir):
                # Copy all files from source_dir to extract_path
                for item in os.listdir(source_dir):
                    s = os.path.join(source_dir, item)
                    d = os.path.join(extract_path, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
    
    # Now check the extracted directory
    if os.path.exists(extract_path):
        # Check for question.txt in the root of the extracted directory
        if os.path.exists(os.path.join(extract_path, "question.txt")):
            return extract_path
            
        # Check for nested directory structure
        nested_path = os.path.join(extract_path, question_dir)
        if os.path.isdir(nested_path) and os.path.exists(os.path.join(nested_path, "question.txt")):
            return nested_path
            
        # Try to find any subfolder that contains question.txt
        for item in os.listdir(extract_path):
            item_path = os.path.join(extract_path, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "question.txt")):
                return item_path
    
    # If no valid path found
    return None

def generate_markdown():
    """Generate markdown file for Anki deck."""
    # Process all 120 questions (001-120)
    question_nums = list(range(1, 121))
    processed_count = 0
    
    # Debug: print total questions to process
    print(f"Processing all {len(question_nums)} questions (001-120)")
    
    # Start writing markdown
    with open(OUTPUT_MD_FILE, 'w', encoding='utf-8') as md_file:
        # Write deck title
        md_file.write("# 腫專2024\n\n")
        
        # Process each question
        for question_num in question_nums:
            # Find the actual directory containing question files
            question_path = find_question_files(question_num)
            if not question_path:
                print(f"Warning: Could not find valid question files for {question_num:03d}")
                continue
                
            processed_count += 1
            
            # Read question content
            question_text = read_file_content(os.path.join(question_path, "question.txt"))
            if not question_text:
                print(f"Warning: No question text found for {question_dir}")
                continue  # Skip if no question text
                
            # Read options
            option_a = read_file_content(os.path.join(question_path, "option_A.txt"))
            option_b = read_file_content(os.path.join(question_path, "option_B.txt"))
            option_c = read_file_content(os.path.join(question_path, "option_C.txt"))
            option_d = read_file_content(os.path.join(question_path, "option_D.txt"))
            option_e = read_file_content(os.path.join(question_path, "option_E.txt"))
            
            # Read correct answer and explanation
            correct_answer = read_file_content(os.path.join(question_path, "correct_answer.txt"))
            explanation = read_file_content(os.path.join(question_path, "explain.txt"))
            
            # Process images
            question_images = process_images(
                os.path.join(question_path, "question_figures"), 
                question_num, 
                "q"
            )
            explain_images = process_images(
                os.path.join(question_path, "explain_figures"), 
                question_num, 
                "e"
            )
            
            # Create question content with proper HTML structure
            question_content = f"<div class=\"card\">\n"
            question_content += f"  <div class=\"question\">\n"
            question_content += f"    <h3>Question {question_num:03d}</h3>\n"
            question_content += f"    <p>{question_text}</p>\n"
            
            # Add question images if any
            for orig_name, new_name in question_images:
                question_content += f"    <img src=\"{new_name}\" alt=\"{orig_name}\">\n"
            
            # Add options
            question_content += f"    <div class=\"options\">\n"
            question_content += f"      <p><strong>A.</strong> {option_a}</p>\n"
            question_content += f"      <p><strong>B.</strong> {option_b}</p>\n"
            question_content += f"      <p><strong>C.</strong> {option_c}</p>\n"
            question_content += f"      <p><strong>D.</strong> {option_d}</p>\n"
            if option_e:
                question_content += f"      <p><strong>E.</strong> {option_e}</p>\n"
            question_content += f"    </div>\n"
            question_content += f"  </div>\n"
            question_content += f"</div>"
            
            # Create answer content with proper HTML structure
            answer_content = f"<div class=\"card\">\n"
            answer_content += f"  <div class=\"question\">\n"
            answer_content += f"    <h3>Question {question_num:03d}</h3>\n"
            answer_content += f"    <p>{question_text}</p>\n"
            
            # Add question images if any
            for orig_name, new_name in question_images:
                answer_content += f"    <img src=\"{new_name}\" alt=\"{orig_name}\">\n"
            
            # Add options
            answer_content += f"    <div class=\"options\">\n"
            answer_content += f"      <p><strong>A.</strong> {option_a}</p>\n"
            answer_content += f"      <p><strong>B.</strong> {option_b}</p>\n"
            answer_content += f"      <p><strong>C.</strong> {option_c}</p>\n"
            answer_content += f"      <p><strong>D.</strong> {option_d}</p>\n"
            if option_e:
                answer_content += f"      <p><strong>E.</strong> {option_e}</p>\n"
            answer_content += f"    </div>\n"
            answer_content += f"  </div>\n"
            answer_content += f"  <hr>\n"
            answer_content += f"  <div class=\"answer\">\n"
            answer_content += f"    <p class=\"correct-answer\">Correct Answer: {correct_answer}</p>\n"
            answer_content += f"    <div class=\"explanation\">\n"
            answer_content += f"      <h4>Explanation:</h4>\n"
            
            # Process explanation text
            explanation_lines = explanation.split('\n')
            for line in explanation_lines:
                if line.strip():
                    # Handle URLs
                    line = re.sub(r'(https?://[^\s]+)', r'<a href="\1">\1</a>', line)
                    answer_content += f"      <p>{line}</p>\n"
            
            # Add explanation images if any
            for orig_name, new_name in explain_images:
                answer_content += f"      <img src=\"{new_name}\" alt=\"{orig_name}\">\n"
            
            answer_content += f"    </div>\n"
            answer_content += f"  </div>\n"
            answer_content += f"</div>"
            
            # Write the card to markdown file
            md_file.write(f"## Question {question_num:03d}\n\n")
            md_file.write(f"{question_content}\n\n")
            md_file.write(f"---\n\n")
            md_file.write(f"{answer_content}\n\n")
            md_file.write("---\n\n")  # Separator between cards
            
            # Add explanation images if any
            for orig_name, new_name in explain_images:
                md_file.write(f"![{orig_name}]({new_name})\n\n")
            
            md_file.write("---\n\n")  # Separator between cards
    
    print(f"Markdown file generated: {OUTPUT_MD_FILE}")
    return processed_count

if __name__ == "__main__":
    # Clean up temp directory if it exists
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Clean up output directory if it exists
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create custom CSS file
    css_file = create_custom_css()
    
    # Generate markdown file
    md_file = generate_markdown()
    
    # Create a dedicated input directory for the markdown file
    md_input_dir = os.path.join(BASE_DIR, "md_input")
    if os.path.exists(md_input_dir):
        shutil.rmtree(md_input_dir)
    os.makedirs(md_input_dir, exist_ok=True)
    
    # Create frontmatter for the markdown file to include custom CSS
    with open(os.path.join(md_input_dir, "anki_deck.md"), 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(f"css: {os.path.basename(css_file)}\n")
        f.write("---\n\n")
        
        # Read the generated markdown file and append it
        with open(md_file, 'r', encoding='utf-8') as src:
            f.write(src.read())
    
    # Copy CSS file to the input directory
    shutil.copy2(css_file, os.path.join(md_input_dir, os.path.basename(css_file)))
    
    # Copy all images to the input directory
    for img in os.listdir(TEMP_DIR):
        shutil.copy2(os.path.join(TEMP_DIR, img), os.path.join(md_input_dir, img))
    
    return processed_count

if __name__ == "__main__":
    # Clean up temp directory if it exists
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Clean up output directory if it exists
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create custom CSS file
    css_file = create_custom_css()
    
    # Generate markdown file
    processed_count = generate_markdown()
    
    # Create a dedicated input directory for the markdown file
    md_input_dir = os.path.join(BASE_DIR, "md_input")
    if os.path.exists(md_input_dir):
        shutil.rmtree(md_input_dir)
    os.makedirs(md_input_dir, exist_ok=True)
    
    # Create frontmatter for the markdown file to include custom CSS
    with open(os.path.join(md_input_dir, "anki_deck.md"), 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(f"css: {os.path.basename(css_file)}\n")
        f.write("---\n\n")
        
        # Read the generated markdown file and append it
        with open(OUTPUT_MD_FILE, 'r', encoding='utf-8') as src:
            f.write(src.read())
    
    # Copy CSS file to the input directory
    shutil.copy2(css_file, os.path.join(md_input_dir, os.path.basename(css_file)))
    
    # Copy all images to the input directory
    for img in os.listdir(TEMP_DIR):
        shutil.copy2(os.path.join(TEMP_DIR, img), os.path.join(md_input_dir, img))
    
    print(f"Successfully processed {processed_count} questions out of 120.")
    print("Now run the following command to create the Anki deck:")
    print(f"source .venv/bin/activate && mdankideck {md_input_dir} {OUTPUT_DIR}")
