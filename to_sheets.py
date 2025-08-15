#!/usr/bin/env python3
"""
Convert normalized questions to Excel format with specified columns.
"""

from pathlib import Path
import pandas as pd
from typing import Dict, Optional


def read_text_file(file_path: Path) -> str:
    """Read text file and return content, return empty string if file doesn't exist."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # Remove control characters (keeping only newlines and tabs)
            content = "".join(
                char for char in content if char.isprintable() or char in "\n\t"
            )
            # Remove empty lines
            lines = [line for line in content.split("\n") if line.strip()]
            return "\n".join(lines)
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""


def process_question_folder(folder_path: Path) -> Optional[Dict[str, str]]:
    """Process a single question folder and return its data as a dictionary."""
    folder_name = folder_path.name

    # Read question text and split into first line and rest
    question_text = read_text_file(folder_path / "question.txt")
    question_lines = question_text.split("\n")
    first_line = question_lines[0] if question_lines else ""
    rest_lines = "\n".join(question_lines[1:]) if len(question_lines) > 1 else ""

    # Read options A through E
    options = {}
    for option in ["A", "B", "C", "D", "E"]:
        option_text = read_text_file(folder_path / f"option_{option}.txt")
        options[f"option{option}"] = option_text

    # Read correct answer and explanation
    correct_answer = read_text_file(folder_path / "correct_answer.txt")
    explain = read_text_file(folder_path / "explain.txt")

    return {
        "folder_name": folder_name,
        "first_line_of_question_txt": first_line,
        "rest_lines_of_question_txt": rest_lines,
        "optionA": options.get("optionA", ""),
        "optionB": options.get("optionB", ""),
        "optionC": options.get("optionC", ""),
        "optionD": options.get("optionD", ""),
        "optionE": options.get("optionE", ""),
        "correct_answer_txt": correct_answer,
        "explain": explain,
    }


def main():
    """Main function to process all question folders and create Excel file."""
    # Set up paths
    base_dir = Path(__file__).parent
    questions_dir = base_dir / "normalized_questions"
    output_file = base_dir / "questions_sheet.xlsx"

    if not questions_dir.exists():
        print(f"Error: {questions_dir} does not exist!")
        return

    # Get all question folders sorted by name
    question_folders = sorted(
        [d for d in questions_dir.iterdir() if d.is_dir() and d.name.isdigit()],
        key=lambda x: int(x.name),
    )

    print(f"Found {len(question_folders)} question folders")

    # Process all folders
    all_data = []
    for folder in question_folders:
        print(f"Processing {folder.name}...", end=" ")
        data = process_question_folder(folder)
        if data:
            all_data.append(data)
            print("✓")
        else:
            print("✗")

    # Create DataFrame and save to Excel
    if all_data:
        df = pd.DataFrame(all_data)

        # Save to Excel with formatting
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Questions", index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets["Questions"]
            for column in df:
                column_length = max(
                    df[column].astype(str).map(len).max(), len(str(column))
                )
                column_length = min(column_length, 50)  # Cap at 50 characters
                col_idx = df.columns.get_loc(column)
                worksheet.column_dimensions[chr(65 + col_idx)].width = column_length + 2

        print(f"\nSuccessfully created Excel file: {output_file}")
        print(f"Total questions processed: {len(all_data)}")
    else:
        print("\nNo data to process!")


if __name__ == "__main__":
    main()
