#!/usr/bin/env python3
"""
Convert normalized questions to Markdown files for mkdocs.
This script takes the normalized questions and generates a folder structure
suitable for mkdocs, with each question in its own folder.
"""

import os
import shutil
import glob
from pathlib import Path

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NORMALIZED_DIR = os.path.join(BASE_DIR, "normalized_questions")
MKDOCS_DIR = os.path.join(BASE_DIR, "mkdocs")

def ensure_dir(directory):
    """Ensure a directory exists, create it if it doesn't."""
    os.makedirs(directory, exist_ok=True)

def create_question_md(question_num, source_dir, target_dir):
    """Create a markdown file for a question."""
    # Ensure target directory exists
    ensure_dir(target_dir)
    
    # Create index.md file path
    index_md_path = os.path.join(target_dir, "index.md")
    
    # Read question content
    question_path = os.path.join(source_dir, "question.txt")
    try:
        with open(question_path, 'r', encoding='utf-8') as f:
            question_content = f.read().strip()
    except FileNotFoundError:
        print(f"Warning: question.txt not found in {source_dir}")
        question_content = "Question content not available"
    
    # Read options
    options = []
    for letter in ['A', 'B', 'C', 'D', 'E']:
        option_path = os.path.join(source_dir, f"option_{letter}.txt")
        try:
            with open(option_path, 'r', encoding='utf-8') as f:
                option_content = f.read().strip()
                if option_content:  # Only add non-empty options
                    options.append((letter, option_content))
        except FileNotFoundError:
            print(f"Warning: option_{letter}.txt not found in {source_dir}")
    
    # Read correct answer
    correct_answer_path = os.path.join(source_dir, "correct_answer.txt")
    try:
        with open(correct_answer_path, 'r', encoding='utf-8') as f:
            correct_answer = f.read().strip()
    except FileNotFoundError:
        print(f"Warning: correct_answer.txt not found in {source_dir}")
        correct_answer = "?"
    
    # Read explanation
    explain_path = os.path.join(source_dir, "explain.txt")
    try:
        with open(explain_path, 'r', encoding='utf-8') as f:
            explanation = f.read().strip()
    except FileNotFoundError:
        print(f"Warning: explain.txt not found in {source_dir}")
        explanation = "No explanation available"
    
    # Check for question figures
    question_figures_dir = os.path.join(source_dir, "question_figures")
    question_figures = []
    if os.path.exists(question_figures_dir):
        question_figures = [os.path.basename(f) for f in glob.glob(os.path.join(question_figures_dir, "*")) 
                           if os.path.isfile(f) and not os.path.basename(f).startswith('.')]
    
    # Check for explanation figures
    explain_figures_dir = os.path.join(source_dir, "explain_figures")
    explain_figures = []
    if os.path.exists(explain_figures_dir):
        explain_figures = [os.path.basename(f) for f in glob.glob(os.path.join(explain_figures_dir, "*")) 
                          if os.path.isfile(f) and not os.path.basename(f).startswith('.')]
    
    # Copy figures to the target directory
    target_figures_dir = os.path.join(target_dir, "figures")
    ensure_dir(target_figures_dir)
    
    # Copy question figures
    if os.path.exists(question_figures_dir):
        for figure in glob.glob(os.path.join(question_figures_dir, "*")):
            if os.path.isfile(figure) and not os.path.basename(figure).startswith('.'):
                shutil.copy2(figure, target_figures_dir)
    
    # Copy explanation figures
    if os.path.exists(explain_figures_dir):
        for figure in glob.glob(os.path.join(explain_figures_dir, "*")):
            if os.path.isfile(figure) and not os.path.basename(figure).startswith('.'):
                shutil.copy2(figure, target_figures_dir)
    
    # Create markdown content
    md_content = [f"# Question\n\n## {question_num:03d}\n"]
    md_content.append(question_content)
    md_content.append("\n")
    
    # Add question figures if any
    if question_figures:
        md_content.append("\n### Question Figures\n")
        for figure in sorted(question_figures):
            figure_name = os.path.splitext(figure)[0]
            md_content.append(f"#### Figure: {figure_name}\n")
            md_content.append(f"![{figure_name}](./figures/{figure})\n")
    
    # Add options
    md_content.append("\n## Options\n")
    for letter, content in options:
        md_content.append(f"- [ ] **{letter}**. {content}\n")
    
    # Add correct answer if available and not empty
    if correct_answer and correct_answer != "?":
        md_content.append(f"\n## Correct Answer \n\n??? note\n    {correct_answer}\n")
    
    # Add explanation
    md_content.append("\n## Explanation\n")
    md_content.append(explanation)
    
    # Add explanation figures if any
    if explain_figures:
        md_content.append("\n### Explanation Figures\n")
        for figure in sorted(explain_figures):
            figure_name = os.path.splitext(figure)[0]
            md_content.append(f"#### Figure: {figure_name}\n")
            md_content.append(f"![{figure_name}](./figures/{figure})\n")
    
    # Write to index.md
    with open(index_md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    
    # Create empty note.md file
    note_md_path = os.path.join(target_dir, "note.md")
    with open(note_md_path, 'w', encoding='utf-8') as f:
        f.write("# Note\n")
    
    return True

def convert_all_questions():
    """Convert all normalized questions to markdown files."""
    # Ensure mkdocs directory exists
    ensure_dir(MKDOCS_DIR)
    
    # Get all question directories
    question_dirs = []
    for item in os.listdir(NORMALIZED_DIR):
        item_path = os.path.join(NORMALIZED_DIR, item)
        if os.path.isdir(item_path) and item.isdigit():
            question_dirs.append((int(item), item_path))
    
    # Sort by question number
    question_dirs.sort()
    
    # Process each question
    for question_num, source_dir in question_dirs:
        print(f"Processing question {question_num:03d}")
        target_dir = os.path.join(MKDOCS_DIR, f"{question_num:03d}")
        create_question_md(question_num, source_dir, target_dir)
    
    print(f"Converted {len(question_dirs)} questions to markdown files in {MKDOCS_DIR}")
    return len(question_dirs)

def main():
    """Main function."""
    print("Converting normalized questions to markdown files for mkdocs...")
    num_converted = convert_all_questions()
    print(f"Completed! Converted {num_converted} questions.")
    print(f"Markdown files are located at: {MKDOCS_DIR}")

if __name__ == "__main__":
    main()
