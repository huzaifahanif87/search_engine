import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os

# only use below one for first tiime
# nltk.download('punkt')
# nltk.download('stopwords')


class Lexicon:
    def __init__(self, lexicon_file="data/lexicon.txt"):
        self.lexicon_file = lexicon_file
        self.lexicon = {}  # Dictionary for word-to-ID mapping
        self.words = []  # List to store words for ID assignment

    def get_index(self, word):
        """Retrieve the index of a word directly from the lexicon dictionary."""
        return self.lexicon.get(word, None)

    def add_word(self, word):
        """Add a word to the lexicon if it's not already present."""
        if word not in self.lexicon:
            self.words.append(word)  

    def save_to_file(self):

        if not os.path.exists(os.path.dirname(self.lexicon_file)):
            os.makedirs(os.path.dirname(self.lexicon_file))

        self.lexicon = {word: idx for idx, word in enumerate(self.words)}

        with open(self.lexicon_file, "w", encoding="utf-8") as lex_file:
            for word, word_id in self.lexicon.items():
                lex_file.write(f"{word_id}:{word}\n")

    def load_from_file(self):
        if os.path.exists(self.lexicon_file):
            with open(self.lexicon_file, "r", encoding="utf-8") as lex_file:
                for line in lex_file:
                    word_id, word = line.strip().split(":")
                    self.lexicon[word] = int(word_id)

