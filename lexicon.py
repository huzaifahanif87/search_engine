
import pandas as pd
import spacy
import os
from concurrent.futures import ProcessPoolExecutor

class Lexicon:
    def __init__(self, lexicon_file="data/lexicon.txt"):
        self.lexicon_file = lexicon_file
        self.words = set()  # Use a set for uniqueness
        self.word_to_id = {} 

    def add_words(self, words):
        self.words.update(words)

    def get_index(self, word):
        return self.word_to_id.get(word)  

    def load_from_file(self):
        if os.path.exists(self.lexicon_file):
            with open(self.lexicon_file, "r", encoding="utf-8") as lex_file:
                for line in lex_file:
                    word_id, word = line.strip().split(":")
                    self.words.add(word)
                    self.word_to_id[word] = int(word_id)
        else:
            print(f"Lexicon file {self.lexicon_file} not found.")

    def save_to_file(self):
        if not os.path.exists(os.path.dirname(self.lexicon_file)):
            os.makedirs(os.path.dirname(self.lexicon_file))
        with open(self.lexicon_file, "w", encoding="utf-8") as lex_file:
            for idx, word in enumerate(sorted(self.words)):  # Sort for consistency
                self.word_to_id[word] = idx
                lex_file.write(f"{idx}:{word}\n")


def tokenize_and_filter(text, nlp, stop_words):
    """Tokenize, lemmatize, and filter text using spaCy."""
    doc = nlp(text.lower())
    # Use lemma_ to get base words, and filter stop words
    return [token.lemma_ for token in doc if token.is_alpha and token.lemma_ not in stop_words]


def process_csv_chunk(chunk, columns, nlp, stop_words):
    """Process a chunk of the CSV and return unique lemmatized words."""
    unique_words = set()
    for column in columns:
        if column in chunk.columns:
            chunk[column].dropna().apply(
                lambda text: unique_words.update(tokenize_and_filter(text, nlp, stop_words))
            )
    return unique_words

def process_csv_to_lexicon(csv_file, lexicon, columns, chunk_size=10000):
    """Process the CSV file in chunks to build the lexicon."""
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])  # Load spaCy model
    stop_words = nlp.Defaults.stop_words

    # Read CSV in chunks and process in parallel
    max_workers = os.cpu_count()  # Use maximum available CPU cores
    print(f"Using {max_workers} workers for processing.")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for chunk in pd.read_csv(csv_file, encoding="ISO-8859-1", chunksize=chunk_size):
            futures.append(executor.submit(process_csv_chunk, chunk, columns, nlp, stop_words))

        # Collect results from all futures
        for future in futures:
            lexicon.add_words(future.result())



if __name__ == "__main__":
    # Path to the CSV file
    csv_file = r"data/sfiftydata.csv"  # Update the path to your dataset

    # Columns to process
    columns_to_process = ["full_content", "content"]

    # Create a Lexicon instance
    lexicon = Lexicon()

    # Process the CSV file and build the lexicon
    process_csv_to_lexicon(csv_file, lexicon, columns_to_process)

    # Save the lexicon
    lexicon.save_to_file()

    print("Lexicon with lemmatized words created and saved successfully!")



