#!/usr/bin/env python3

import os
from pathlib import Path


def read_file(filepath):
    """Read and return the content of a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def create_anki_card(question_dir, question_num):
    """Create an Anki card in markdown-anki-decks format from a question directory."""
    # Read all components
    question = read_file(question_dir / "question.txt")
    option_a = read_file(question_dir / "option_A.txt")
    option_b = read_file(question_dir / "option_B.txt")
    option_c = read_file(question_dir / "option_C.txt")
    option_d = read_file(question_dir / "option_D.txt")
    option_e = read_file(question_dir / "option_E.txt")
    correct_answer = read_file(question_dir / "correct_answer.txt")
    explanation = read_file(question_dir / "explain.txt")

    # Clean the question number prefix if present
    if question.startswith(f"{question_num}→"):
        question = question[len(f"{question_num}→") :].strip()

    # Format the card with all front elements in H2
    card = f"""<h2 markdown="block" style="font-size: 16px;">
{question_num:03d}

{question}

**選項：**

- A. {option_a}

- B. {option_b}

- C. {option_c}

- D. {option_d}

- E. {option_e}
</h2>

**正確答案：{correct_answer}**

**解釋：**
{explanation}"""

    return card


def main():
    # Path to normalized questions directory
    questions_dir = Path("normalized_questions")

    # Create output directory for markdown files
    output_dir = Path("anki_markdown_decks")
    output_dir.mkdir(exist_ok=True)

    # Get all question directories and sort them numerically
    question_dirs = [d for d in questions_dir.iterdir() if d.is_dir()]
    question_dirs.sort(key=lambda x: int(x.name))

    # Create markdown content
    cards = []

    # Add deck title
    cards.append("# Medical Questions\n")

    for q_dir in question_dirs:
        try:
            question_num = int(q_dir.name)
            card = create_anki_card(q_dir, question_num)
            cards.append(card)
            print(f"Processed question {q_dir.name}")
        except Exception as e:
            print(f"Error processing question {q_dir.name}: {e}")
            continue

    # Join all cards
    markdown_content = "\n\n".join(cards)

    # Write to output file
    output_path = output_dir / "medical_questions.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"\nSuccessfully created {output_path} with {len(cards) - 1} cards")

    # Now convert to Anki deck using markdown-anki-decks
    print("\nConverting to Anki deck...")
    os.system(f"source .venv/bin/activate && mdankideck {output_dir} .")

    print("\nAnki deck should be created as medical_questions.apkg")


if __name__ == "__main__":
    main()
