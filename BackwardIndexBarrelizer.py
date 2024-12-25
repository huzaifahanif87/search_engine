import pickle
import os
from collections import defaultdict
from math import log
from BackwardIndex import *



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
        doc_count = sum(len(doc_data) for doc_data in backward_index.values())  
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


    def find_barrel_id(self, word_id):
        """Find the barrel ID for a given word ID."""
        return word_id // self.words_per_barrel

    def load_barrel(self, barrel_id):
        """Load a barrel from the pickle file."""
        barrel_file = os.path.join(self.output_dir, f"backward_barrel_{barrel_id}.pkl")
        if not os.path.exists(barrel_file):
            return {}  # Return an empty dictionary if the barrel does not exist
        with open(barrel_file, "rb") as f:
            return pickle.load(f)
    def update_barrels(self, updated_word_ids):
        """Update barrels based on a list of updated word IDs."""
        backward_index = self.load_backward_index()

        # Group updated word IDs by their respective barrel IDs
        barrel_updates = defaultdict(list)
        for word_id in updated_word_ids:
            barrel_id = self.find_barrel_id(word_id)
            barrel_updates[barrel_id].append(word_id)

        # Process each barrel
        for barrel_id, word_ids in barrel_updates.items():
            print(f"Updating barrel {barrel_id}...")

            # Load the barrel, or create a new one if it doesn't exist
            barrel_data = self.load_barrel(barrel_id)

            # Update or add the word data in the barrel
            for word_id in word_ids:
                if word_id in backward_index:
                    barrel_data[word_id] = backward_index[word_id]

            # Save the updated barrel
            self.save_barrel(barrel_id, barrel_data)
if __name__ == "__main__":
    # Create a BackwardIndex instance (assuming the backward index is already created)
    # backward_indexer = BackwardIndex()

    # # Step 1: Create backward index (from forward index)
    # backward_indexer.create_backward_index()

    # # Step 2: Create barrels from the backward index
    # barrelizer = BackwardIndexBarrelizer(backward_index_file="indexes/backwardindex.pkl")
    # barrelizer.create_barrels()

    barrelizer = BackwardIndexBarrelizer()

    # Assume these word IDs were updated in the backward index
    updated_word_ids = [155426]  # Example word IDs

    # Update the barrels with the updated word IDs
    barrelizer.update_barrels(updated_word_ids)