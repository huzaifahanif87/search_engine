
import pandas as pd
import pickle
import spacy
from concurrent.futures import ProcessPoolExecutor
from lexicon import Lexicon  # Your Lexicon class
class ForwardIndex:
    def __init__(self, csv_file, lexicon_file="data/lexicon.txt", output_file="indexes/forward_index.pkl"):
        self.csv_file = csv_file
        self.lexicon_file = lexicon_file
        self.output_file = output_file
        self.columns_to_process = {"content": 1, "full_content": 1, "description": 2, "title": 3}
        self.chunk_size = 1000
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.lexicon = Lexicon(self.lexicon_file)
        self.lexicon.load_from_file()

    def process_chunk(self, chunk):
        """
        Process a chunk of data to generate a partial forward index.
        """
        partial_index = {}
        for doc_id, row in chunk.iterrows():
            partial_index[doc_id] = {"words": [], "tf": {}}

            for column, weight in self.columns_to_process.items():
                if column in row and isinstance(row[column], str):
                    # Tokenize and lemmatize the text
                    doc = self.nlp(row[column].lower())
                    words = [token.lemma_ for token in doc if token.is_alpha]

                    # Process positions and assign weights
                    for position, word in enumerate(words):
                        word_id = self.lexicon.get_index(word)
                        if word_id is not None:
                            # Save word ID and position
                            partial_index[doc_id]["words"].append((word_id, position))

                            # Update term frequency with weight
                            if word_id not in partial_index[doc_id]["tf"]:
                                partial_index[doc_id]["tf"][word_id] = 0
                            partial_index[doc_id]["tf"][word_id] += weight

        return partial_index

    def merge_indexes(self, indexes):
        """
        Merge partial indexes into a single forward index.
        """
        merged_index = {}
        for partial_index in indexes:
            for doc_id, data in partial_index.items():
                if doc_id not in merged_index:
                    merged_index[doc_id] = {"words": [], "tf": {}}
                merged_index[doc_id]["words"].extend(data["words"])
                for word_id, count in data["tf"].items():
                    if word_id not in merged_index[doc_id]["tf"]:
                        merged_index[doc_id]["tf"][word_id] = 0
                    merged_index[doc_id]["tf"][word_id] += count
        return merged_index

    def create_forward_index(self):
        """
        Generate a forward index with word positions and weighted term frequencies using multi-processing.
        """
        forward_index = {}
        indexes = []

        # Read and process the CSV in chunks
        with ProcessPoolExecutor() as executor:
            futures = []
            for chunk in pd.read_csv(self.csv_file, encoding="ISO-8859-1", chunksize=self.chunk_size):
                futures.append(executor.submit(self.process_chunk, chunk))
            
            # Collect results
            for future in futures:
                indexes.append(future.result())

        # Merge all partial indexes
        forward_index = self.merge_indexes(indexes)

        # Save the forward index to a pickle file
        with open(self.output_file, "wb") as f:
            pickle.dump(forward_index, f)

        print(f"Forward index with positions and weighted term frequencies created and saved to {self.output_file}.")

    def load_forward_index(self):
        """Load the forward index from a pickle file."""
        with open(self.output_file, "rb") as f:
            forward_index = pickle.load(f)
        return forward_index

    def print_forward_index(self, forward_index):
        """Print the forward index contents."""
        for doc_id, data in forward_index.items():
            print(f"Document ID: {doc_id}")
            print(f"\tWords: {data['words']}")
            print(f"\tTerm Frequency (TF): {data['tf']}")
            print("-" * 40)  # Separator for readability


if __name__ == "__main__":
    # Path to your dataset
    csv_file = r"data/sfiftydata.csv"
    
    # Create a ForwardIndex instance
    forward_indexer = ForwardIndex(csv_file)
    
    # Create the forward index from the dataset
    # forward_indexer.create_forward_index()

    # Load and print the forward index (if needed)
    forward_index = forward_indexer.load_forward_index()
    forward_indexer.print_forward_index(forward_index)
