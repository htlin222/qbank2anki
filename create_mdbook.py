#!/usr/bin/env python3
"""
Script to create an mdBook structure from normalized questions.
Each question becomes a separate chapter in the mdBook.
"""

import os
import re
import shutil
import glob
from pathlib import Path
import natsort  # For natural sorting of filenames

def ensure_dir(directory):
    """Ensure that a directory exists, creating it if necessary."""
    os.makedirs(directory, exist_ok=True)

def create_book_toml(book_dir, title="Question Collection"):
    """Create the book.toml configuration file for mdBook."""
    toml_content = f"""[book]
title = "{title}"
authors = ["Generated"]
description = "A collection of questions organized as an mdBook"
language = "zh-TW"

[output.html]
default-theme = "light"
preferred-dark-theme = "navy"
curly-quotes = true
mathjax-support = true
"""
    with open(os.path.join(book_dir, "book.toml"), "w", encoding="utf-8") as f:
        f.write(toml_content)

def read_normalized_questions(normalized_dir):
    """Read questions from the normalized_questions directory."""
    questions = []
    question_dirs = sorted(glob.glob(os.path.join(normalized_dir, "*")))
    
    for question_dir in question_dirs:
        if not os.path.isdir(question_dir):
            continue
            
        question_num = os.path.basename(question_dir)
        
        # Read question content
        question_file = os.path.join(question_dir, "question.txt")
        if not os.path.exists(question_file):
            continue
            
        with open(question_file, "r", encoding="utf-8") as f:
            question_content = f.read().strip()
        
        # Read options
        options = {}
        for option in ["A", "B", "C", "D", "E"]:
            option_file = os.path.join(question_dir, f"option_{option}.txt")
            if os.path.exists(option_file):
                with open(option_file, "r", encoding="utf-8") as f:
                    option_content = f.read().strip()
                    if option_content:  # Only add non-empty options
                        options[option] = option_content
        
        # Read correct answer
        answer_file = os.path.join(question_dir, "correct_answer.txt")
        correct_answer = "?"
        if os.path.exists(answer_file):
            with open(answer_file, "r", encoding="utf-8") as f:
                correct_answer = f.read().strip()
        
        # Read explanation
        explain_file = os.path.join(question_dir, "explain.txt")
        explanation = ""
        if os.path.exists(explain_file):
            with open(explain_file, "r", encoding="utf-8") as f:
                explanation = f.read().strip()
        
        # Check for figures
        question_figures = []
        question_figures_dir = os.path.join(question_dir, "question_figures")
        if os.path.exists(question_figures_dir) and os.path.isdir(question_figures_dir):
            question_figures = [f for f in os.listdir(question_figures_dir) 
                              if os.path.isfile(os.path.join(question_figures_dir, f))]
            # Sort figures in natural numerical order (figure1, figure9, figure12, etc.)
            try:
                question_figures = natsort.natsorted(question_figures)
            except ImportError:
                # Fallback sorting method if natsort is not available
                def natural_sort_key(s):
                    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
                question_figures.sort(key=natural_sort_key)
            
        explain_figures = []
        explain_figures_dir = os.path.join(question_dir, "explain_figures")
        if os.path.exists(explain_figures_dir) and os.path.isdir(explain_figures_dir):
            explain_figures = [f for f in os.listdir(explain_figures_dir) 
                             if os.path.isfile(os.path.join(explain_figures_dir, f))]
            # Sort figures in natural numerical order (figure1, figure9, figure12, etc.)
            try:
                explain_figures = natsort.natsorted(explain_figures)
            except ImportError:
                # Fallback sorting method if natsort is not available
                def natural_sort_key(s):
                    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
                explain_figures.sort(key=natural_sort_key)
        
        # Format the question content for mdBook
        formatted_question = f"## Question {question_num}\n\n{question_content}\n\n"
        
        # Add question figures if any
        if question_figures:
            formatted_question += "\n**Question Figures:**\n\n"
            for fig in question_figures:
                # Create a relative path for the image that will work in mdBook
                fig_path = f"../normalized_questions/{question_num}/question_figures/{fig}"
                # Add image filename as level 4 header before the image reference
                formatted_question += f"#### {fig}\n\n![{fig}]({fig_path})\n\n"
        
        # Add options
        formatted_question += "\n**Options:**\n\n"
        for option, content in sorted(options.items()):
            formatted_question += f"**{option}:** {content}\n\n\n"
        
        # Add correct answer
        formatted_question += f"\n**Correct Answer:** {correct_answer}\n\n\n"
        
        # Add explanation
        if explanation:
            formatted_question += "\n**Explanation:**\n\n"
            formatted_question += f"{explanation}\n\n"
        
        # Add explanation figures if any
        if explain_figures:
            formatted_question += "\n**Explanation Figures:**\n\n"
            for fig in explain_figures:
                # Create a relative path for the image that will work in mdBook
                fig_path = f"../normalized_questions/{question_num}/explain_figures/{fig}"
                # Add image filename as level 4 header before the image reference
                formatted_question += f"#### {fig}\n\n![{fig}]({fig_path})\n\n"
        
        questions.append(formatted_question)
    
    return "", questions  # Empty header, list of formatted questions

def create_summary_md(book_src_dir, questions):
    """Create the SUMMARY.md file that defines the book's structure."""
    summary_content = "# Summary\n\n"
    
    for i, question in enumerate(questions, 1):
        # Extract the question number from the header
        match = re.search(r'## Question (\d+)', question)
        if match:
            question_num = match.group(1).zfill(3)  # Ensure 3-digit format
        else:
            question_num = str(i).zfill(3)
        
        summary_content += f"- [Question {int(question_num)}](question_{question_num}.md)\n"
    
    with open(os.path.join(book_src_dir, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write(summary_content)

def create_readme_md(book_src_dir, header):
    """Create the README.md file that serves as the introduction."""
    readme_content = "# Introduction\n\n"
    if header:
        readme_content += header + "\n\n"
    readme_content += "This is a collection of questions organized as an mdBook."
    
    with open(os.path.join(book_src_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

def write_question_files(book_src_dir, questions):
    """Write each question to its own markdown file."""
    for question in questions:
        # Extract the question number from the header
        match = re.search(r'## Question (\d+)', question)
        if match:
            question_num = match.group(1).zfill(3)  # Ensure 3-digit format
            # Replace the original header with a level 1 header for the mdBook chapter
            question_content = re.sub(r'## Question \d+.*?(\n|$)', f'# Question {int(question_num)}\n', question, 1)
        else:
            # If no question number is found, use a sequential number
            question_num = str(len(os.listdir(book_src_dir)) + 1).zfill(3)
            question_content = f'# Question {int(question_num)}\n\n{question}'
        
        # Write the question to its own file
        with open(os.path.join(book_src_dir, f"question_{question_num}.md"), "w", encoding="utf-8") as f:
            f.write(question_content)

def main():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    normalized_dir = os.path.join(base_dir, "normalized_questions")
    book_dir = os.path.join(base_dir, "mdbook")
    book_src_dir = os.path.join(book_dir, "src")
    
    # Try to install natsort if not available
    try:
        import natsort
    except ImportError:
        print("Installing natsort package for better filename sorting...")
        try:
            import subprocess
            subprocess.check_call(["uv", "pip", "install", "natsort"])
            import natsort
            print("Successfully installed natsort")
        except Exception as e:
            print(f"Could not install natsort: {e}")
            print("Will use fallback sorting method")
    
    # Ensure the mdBook directory structure exists
    ensure_dir(book_dir)
    ensure_dir(book_src_dir)
    
    # Read questions from the normalized_questions directory
    header, questions = read_normalized_questions(normalized_dir)
    
    # Create the mdBook files
    create_book_toml(book_dir, title="Normalized Questions Collection")
    create_summary_md(book_src_dir, questions)
    create_readme_md(book_src_dir, header)
    write_question_files(book_src_dir, questions)
    
    print(f"mdBook structure created at {book_dir}")
    print(f"Total questions processed: {len(questions)}")
    print("Run 'mdbook serve' in the mdbook directory to view the book.")
    
    # Create a symlink to the normalized_questions directory for images
    normalized_link = os.path.join(book_src_dir, "normalized_questions")
    if not os.path.exists(normalized_link):
        # Use relative path for the symlink target
        rel_path = os.path.relpath(normalized_dir, book_src_dir)
        os.symlink(rel_path, normalized_link, target_is_directory=True)
        print(f"Created symlink to normalized_questions for images")
    else:
        print(f"Symlink to normalized_questions already exists")

if __name__ == "__main__":
    main()
