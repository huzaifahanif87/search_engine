import pandas as pd
import spacy
import pickle
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from math import log
from ForwardIndex import ForwardIndex

class ForwardIndexBarrelizer:
    def __init__(self, forward_index_file="indexes/forwardindex.pkl", output_dir="forward_barrels", docs_per_barrel=5000):
        self.forward_index_file = forward_index_file
        self.output_dir = output_dir
        self.docs_per_barrel = docs_per_barrel
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load_forward_index(self):
        """Load the forward index from the pickle file."""
        with open(self.forward_index_file, "rb") as f:
            return pickle.load(f)

    def calculate_tfidf_for_doc(self, doc_data, doc_count, word_doc_frequency):
        """Calculate TF-IDF for a single document."""
        tfidf_data = {}
        for word_id, tf in doc_data["tf"].items():
            df = word_doc_frequency.get(word_id, 0)
            if df > 0:
                tfidf = tf * log(doc_count / (1 + df))  # TF-IDF calculation
                tfidf_data[word_id] = tfidf
        return doc_data["words"], tfidf_data

    def calculate_tfidf(self, forward_index):
        """Calculate TF-IDF for all documents in the forward index."""
        doc_count = len(forward_index)
        
        # Step 1: Calculate document frequency (DF) for each word
        word_doc_frequency = defaultdict(int)
        for doc_id, data in forward_index.items():
            unique_words = set(word_id for word_id, _ in data["words"])
            for word_id in unique_words:
                word_doc_frequency[word_id] += 1
        
        # Step 2: Calculate TF-IDF for each document in parallel
        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(self.calculate_tfidf_for_doc, doc_data, doc_count, word_doc_frequency)
                for doc_data in forward_index.values()
            ]
            for future in futures:
                words, tfidf_data = future.result()
                for doc_id, data in forward_index.items():
                    data["tfidf"] = tfidf_data
        return forward_index

    def save_barrel(self, barrel_id, barrel_data):
        """Save a barrel to a pickle file."""
        barrel_file = os.path.join(self.output_dir, f"forward_barrel_{barrel_id}.pkl")
        with open(barrel_file, "wb") as f:
            pickle.dump(barrel_data, f)
        print(f"Forward barrel {barrel_id} saved.")

    def create_barrels(self):
        """Divide the forward index into barrels and calculate TF-IDF."""
        forward_index = self.load_forward_index()
        forward_index = self.calculate_tfidf(forward_index)  # Calculate TF-IDF scores

        # Create barrels and store in the output directory
        barrel_id = 0
        barrel_data = {}
        for doc_id, data in forward_index.items():
            barrel_data[doc_id] = data

            # If the number of documents exceeds the threshold, save the barrel
            if len(barrel_data) >= self.docs_per_barrel:
                self.save_barrel(barrel_id, barrel_data)
                barrel_id += 1
                barrel_data = {}

        # Save the last barrel if it has remaining documents
        if barrel_data:
            self.save_barrel(barrel_id, barrel_data)

# Usage
if __name__ == "__main__":
    # Path to your dataset
    csv_file = "data/sfiftydata.csv"
    lexicon_file = "data/lexicon.txt"  # Make sure to have this file
    
    forward_indexer = ForwardIndex(csv_file, lexicon_file)
    forward_indexer.create_forward_index()  # Step 1: Create forward index

    # Step 2: Create barrels from the forward index
    barrelizer = ForwardIndexBarrelizer(forward_index_file="indexes/forwardindex.pkl")
    barrelizer.create_barrels()
