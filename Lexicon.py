import pandas as pd
import spacy
import os
from concurrent.futures import ProcessPoolExecutor

class Lexicon:
    def __init__(self, lexicon_file="data/lexicon.txt"):
        self.lexicon_file = lexicon_file
        self.words = set()  # Set for uniqueness
        self.word_to_id = {}

    def add_words(self, words):
        """Add new words to the lexicon."""
        self.words.update(words)

    def get_index(self, word):
        """Get the ID of a word."""
        return self.word_to_id.get(word)

    def load_from_file(self):
        """Load words and their ids from lexicon file."""
        if os.path.exists(self.lexicon_file):
            with open(self.lexicon_file, "r", encoding="utf-8") as lex_file:
                for line in lex_file:
                    word_id, word = line.strip().split(":")
                    self.words.add(word)
                    self.word_to_id[word] = int(word_id)
        else:
            print(f"Lexicon file {self.lexicon_file} not found.")

    def save_to_file(self):
        """Save the lexicon to a file, appending new words at the end."""
        if not os.path.exists(os.path.dirname(self.lexicon_file)):
            os.makedirs(os.path.dirname(self.lexicon_file))

        # Calculate the starting ID for new words (next available ID)
        starting_id = max(self.word_to_id.values(), default=-1) + 1  # Get max ID and increment by 1

        with open(self.lexicon_file, "a", encoding="utf-8") as lex_file:
            for word in self.words:
                if word not in self.word_to_id:
                    self.word_to_id[word] = starting_id
                    lex_file.write(f"{self.word_to_id[word]}:{word}\n")
                    starting_id += 1  # Increment ID for the next word

    def get_all_words(self):
        """Return all words in the lexicon."""
        return self.words

    def add_stop_words(self, stop_words):
        """Add stop words to the lexicon."""
        self.stop_words = stop_words

def update_lexicon(csv_file, lexicon, chunk_size=10000):
    """Update lexicon with new document data."""
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])  # Load spaCy model
    columns = ["full_content", "content", "title", "description", "url"]  

    # Collect stop words from spaCy model
    stop_words = nlp.Defaults.stop_words
    lexicon.add_stop_words(stop_words)

    # Load existing lexicon into memory
    lexicon.load_from_file()

    # Collect existing words into a set for fast lookup
    existing_words = lexicon.get_all_words()

    max_workers = os.cpu_count()  # Use maximum available CPU cores
    print(f"Using {max_workers} workers for processing.")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for chunk in pd.read_csv(csv_file, encoding="ISO-8859-1", chunksize=chunk_size):
            futures.append(executor.submit(process_csv_chunk, chunk, columns, nlp, existing_words))

        # Collect results from all futures
        all_new_words = set()
        for future in futures:
            all_new_words.update(future.result())

        # Add new words to the lexicon
        lexicon.add_words(all_new_words)

    # Save the updated lexicon
    lexicon.save_to_file()

    print("Lexicon updated and saved successfully!")



def tokenize_and_filter(text, nlp):
    """Tokenize and lemmatize text using spaCy, including all words."""
    doc = nlp(text.lower())
    return [token.lemma_ for token in doc if token.is_alpha]  # Return lemmas of all alphabetic tokens


def process_csv_chunk(chunk, columns, nlp, existing_words):
    """Process a chunk of the CSV and return unique lemmatized words that are not in the lexicon."""
    unique_words = set()
    for column in columns:
        if column in chunk.columns:
            chunk[column].dropna().apply(
                lambda text: unique_words.update(tokenize_and_filter(text, nlp))  # Get lemmatized tokens
            )
    
    # Filter out words that already exist in the lexicon
    new_words = unique_words - existing_words
    return new_words





if __name__ == "__main__":
    # Path to the CSV file
    csv_file = r"data/sampleData.csv"  # Update with your CSV file path

    # Columns to process

    # Create a Lexicon instance
    lexicon = Lexicon()

    # Update the lexicon with new data
    update_lexicon(csv_file, lexicon)

    print("Lexicon with new words added successfully!")
