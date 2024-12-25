import pandas as pd
import spacy
import pickle
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from math import log

from Lexicon import Lexicon


def default_forward_index():
    return {"words": [], "tf": defaultdict(int)}

class ForwardIndex:
    def __init__(self, csv_file, lexicon, output_file="indexes/forwardindex.pkl", chunk_size=2000):
        self.csv_file = csv_file
        self.output_file = output_file
        self.chunk_size = chunk_size
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.lexicon = lexicon 
    def load_forward_index(filepath):
        """Load the forward index from the pickle file."""
        with open(filepath, "rb") as f:
            return pickle.load(f)
    def get_unique_word_ids(self, doc_ids):
        """Return unique word IDs corresponding to the given list of document IDs."""
        # Load the forward index
        with open(self.output_file, "rb") as f:
            forward_index = pickle.load(f)
        
        unique_word_ids = set()  # Use a set to ensure uniqueness
        
        # Iterate over the given document IDs
        for doc_id in doc_ids:
            if doc_id in forward_index:
                # Extract word IDs from the document's "words" field
                for word_id, _ in forward_index[doc_id]["words"]:
                    unique_word_ids.add(word_id)
        
        return list(unique_word_ids)
    def _get_last_document_id(self):
        """Get the last document ID from the current forward index or lexicon."""
        if os.path.exists(self.output_file):
            with open(self.output_file, "rb") as f:
                forward_index = pickle.load(f)
                return max(forward_index.keys(), default=-1)  # Get the highest document ID
        return -1  # If no documents exist, start from 0

    def process_chunk(self, chunk, starting_doc_id):
        """Process a chunk of documents to create a forward index."""
        forward_index = defaultdict(default_forward_index)  
        column_weights = {
            "title": 4,  # Title column gets a weight of 4
            "url": 3,    # URL column gets a weight of 3
            "description": 2,  # Description column gets a weight of 2
            "content": 1,  # Content column gets a weight of 1
            "full_content": 1,  # Full content column gets a weight of 1
        }

        doc_id_counter = starting_doc_id + 1  # Start assigning document IDs from this point

        for _, row in chunk.iterrows():
            doc_id = doc_id_counter  # Assign a new document ID
            doc_id_counter += 1  # Increment the document ID for the next document
            
            for col in ["url", "description", "title", "content", "full_content"]:  
                if pd.notna(row[col]):
                    words = [token.lemma_ for token in self.nlp(row[col].lower()) if token.is_alpha]
                    weight = column_weights.get(col, 1)  # Get the weight based on the column, default is 1
                    
                    for pos, word in enumerate(words):
                        word_id = self.lexicon.get_index(word)  # Use lexicon to get word ID
                        if word_id is not None:
                            forward_index[doc_id]["words"].append((word_id, pos))
                            forward_index[doc_id]["tf"][word_id] += weight  # Add weight for frequency
        
        return forward_index

    def update_forward_index(self):
        """Update forward index by appending new documents with new IDs."""
        # Get the last document ID from the existing forward index
        last_doc_id = self._get_last_document_id()

        forward_index = defaultdict(default_forward_index)  # Initialize new forward index
        
        # Use ProcessPoolExecutor to process chunks in parallel
        with ProcessPoolExecutor() as executor:
            futures = []
            chunks = pd.read_csv(self.csv_file, chunksize=self.chunk_size)
            for chunk in chunks:
                futures.append(executor.submit(self.process_chunk, chunk, last_doc_id))
            
            # Collect results from the parallel processing
            for future in futures:
                partial_index = future.result()
                for doc_id, data in partial_index.items():
                    forward_index[doc_id]["words"].extend(data["words"])
                    for word_id, count in data["tf"].items():
                        forward_index[doc_id]["tf"][word_id] += count
        
        # Load the existing forward index (if exists) and append new data
        if os.path.exists(self.output_file):
            with open(self.output_file, "rb") as f:
                existing_forward_index = pickle.load(f)
                # Append new documents to the existing forward index
                forward_index.update(existing_forward_index)

        # Save the updated forward index with new documents appended
        with open(self.output_file, "wb") as f:
            pickle.dump(forward_index, f)
        print(f"Forward index updated and saved to {self.output_file}.")


def main():
    """Main function to update the forward index with new documents."""
    # Path to the CSV file
    csv_file = r"data/sampleData.csv"  # Update with your CSV file path

    # Path to the lexicon file
    lexicon = Lexicon("data/lexicon.txt")  # Update with your lexicon file path
    lexicon.load_from_file()
    # Path to the output forward index file
    output_file = r"indexes/forwardindex.pkl"  # Update with your desired output path for forward index

    # Create an instance of ForwardIndex
    forward_index = ForwardIndex(csv_file, lexicon, output_file)

    # Update the forward index with new data from the CSV file
    forward_index.update_forward_index()

    print("Forward index updated successfully!")

# Call the main function to run the update process
if __name__ == "__main__":
    main()
