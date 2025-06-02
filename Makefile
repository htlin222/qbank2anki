.PHONY: all clean extract normalize anki mkdocs

all: extract normalize anki mkdocs

extract:
@echo "Extracting and normalizing questions..."
python3 extract_and_normalize.py

normalize: extract
@echo "Normalization completed."

anki: normalize
@echo "Generating Anki deck..."
python3 generate_anki_deck.py

mkdocs: normalize
@echo "Generating mkdocs files..."
python3 txt2md.py

clean:
@echo "Cleaning up..."
rm -rf normalized_questions
rm -rf mkdocs
@echo "Cleanup completed."
