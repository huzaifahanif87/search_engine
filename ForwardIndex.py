import pandas as pd
import spacy
import pickle
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from math import log

from Lexicon import Lexicon

# Default factory function for defaultdict to avoid lambda pickling issues
def default_forward_index():
    return {"words": [], "tf": defaultdict(int)}

class ForwardIndex:
    def __init__(self, csv_file, lexicon_file, output_file="indexes/forwardindex.pkl", chunk_size=2000):
        self.csv_file = csv_file
        self.lexicon_file = lexicon_file
        self.output_file = output_file
        self.chunk_size = chunk_size
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.lexicon = Lexicon(self.lexicon_file)  # Create Lexicon object
        self.lexicon.load_from_file()

    def process_chunk(self, chunk):
        print(f"Processing chunk with {len(chunk)} documents")
        """Process a chunk of documents to create a forward index."""
        forward_index = defaultdict(default_forward_index)  # Use the function here instead of lambda
        
        # Column-specific weights
        column_weights = {
            "title": 4,  # Title column gets a weight of 3
            "url": 3,    # URL column gets a weight of 2
            "description": 2,  # Description column gets a weight of 2
            "content": 1,  # Content column gets a weight of 1
            "full_content": 1,  # Full content column gets a weight of 1
        }

        for doc_id, row in chunk.iterrows():
            for col in [ "url",  "description", "title","content", "full_content"]:  # Process columns of interest
                if pd.notna(row[col]):
                    words = [token.lemma_ for token in self.nlp(row[col].lower()) if token.is_alpha]
                    weight = column_weights.get(col, 1)  # Get the weight based on the column, default is 1
                    
                    for pos, word in enumerate(words):
                        word_id = self.lexicon.get_index(word)  # Use lexicon to get word ID
                        if word_id is not None:
                            forward_index[doc_id]["words"].append((word_id, pos))
                            forward_index[doc_id]["tf"][word_id] += weight  # Add weight for frequency
        
        print(f"Processed chunk with {len(forward_index)} entries")
        return forward_index


    def create_forward_index(self):
        """Create the forward index and store basic information for barrel creation."""
        forward_index = defaultdict(default_forward_index)  # Use the function here instead of lambda
        
        # Use ProcessPoolExecutor to process chunks in parallel
        with ProcessPoolExecutor() as executor:
            futures = []
            chunks = pd.read_csv(self.csv_file, chunksize=self.chunk_size)
            for chunk in chunks:
                futures.append(executor.submit(self.process_chunk, chunk))
            
            # Collect results from the parallel processing
            for future in futures:
                partial_index = future.result()
                for doc_id, data in partial_index.items():
                    forward_index[doc_id]["words"].extend(data["words"])
                    for word_id, count in data["tf"].items():
                        forward_index[doc_id]["tf"][word_id] += count
        
        # Save forward index for further processing
        with open(self.output_file, "wb") as f:
            pickle.dump(forward_index, f)
        print(f"Forward index created and saved to {self.output_file}.")
