import pickle
import os
from collections import defaultdict
from math import log
from BackwardIndex import BackwardIndex



class BackwardIndexBarrelizer:
    def __init__(self, backward_index_file="indexes/backwardindex.pkl", output_dir="backward_barrels", words_per_barrel=5000):
        self.backward_index_file = backward_index_file
        self.output_dir = output_dir
        self.words_per_barrel = words_per_barrel
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load_backward_index(self):
        """Load the backward index from a pickle file."""
        with open(self.backward_index_file, "rb") as f:
            return pickle.load(f)

    def calculate_tfidf_for_word(self, word_data, doc_count, word_doc_frequency):
        """Calculate TF-IDF for a word across documents."""
        tfidf_data = {}
        for doc_id, doc_info in word_data.items():
            tf = doc_info["tf"]
            df = word_doc_frequency.get(doc_id, 0)
            if df > 0:
                tfidf = tf * log(doc_count / (1 + df))  # TF-IDF calculation
                tfidf_data[doc_id] = tfidf
        return tfidf_data

    def calculate_tfidf(self, backward_index):
        """Calculate TF-IDF for all words in the backward index."""
        doc_count = sum(len(doc_data) for doc_data in backward_index.values())  # Total number of docs
        word_doc_frequency = defaultdict(int)

        # Step 1: Calculate document frequency (DF) for each word
        for word_id, doc_data in backward_index.items():
            for doc_id in doc_data:
                word_doc_frequency[doc_id] += 1

        # Step 2: Calculate TF-IDF for each word (word_id)
        for word_id, doc_data in backward_index.items():
            tfidf_data = self.calculate_tfidf_for_word(doc_data, doc_count, word_doc_frequency)
            for doc_id, tfidf in tfidf_data.items():
                backward_index[word_id][doc_id]["tfidf"] = tfidf

        return backward_index


    def save_barrel(self, barrel_id, barrel_data):
        """Save a barrel to a pickle file."""
        # Sort words in the barrel_data by word_id
        sorted_barrel_data = {word_id: barrel_data[word_id] for word_id in sorted(barrel_data)}

        # Save sorted barrel
        barrel_file = os.path.join(self.output_dir, f"backward_barrel_{barrel_id}.pkl")
        with open(barrel_file, "wb") as f:
            pickle.dump(sorted_barrel_data, f)
        print(f"Backward barrel {barrel_id} saved.")

    def create_barrels(self):
        """Divide the backward index into barrels and save them."""
        backward_index = self.load_backward_index()
        backward_index = self.calculate_tfidf(backward_index)  # Calculate TF-IDF for backward index

        # Create barrels and store in the output directory
        barrel_id = 0
        barrel_data = {}
        for word_id, doc_data in backward_index.items():
            barrel_data[word_id] = doc_data

            # If the number of words exceeds the threshold, save the barrel
            if len(barrel_data) >= self.words_per_barrel:
                self.save_barrel(barrel_id, barrel_data)
                barrel_id += 1
                barrel_data = {}

        # Save the last barrel if it has remaining words
        if barrel_data:
            self.save_barrel(barrel_id, barrel_data)

# Usage
if __name__ == "__main__":
    # Create a BackwardIndex instance (assuming the backward index is already created)
    backward_indexer = BackwardIndex()

    # Step 1: Create backward index (from forward index)
    backward_indexer.create_backward_index()

    # Step 2: Create barrels from the backward index
    barrelizer = BackwardIndexBarrelizer(backward_index_file="indexes/backwardindex.pkl")
    barrelizer.create_barrels()
