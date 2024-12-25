
import pickle
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor


def default_doc_dict():
    """Default dictionary structure for backward index."""
    return {"positions": [], "tf": 0}


def default_word_dict():
    """Default dictionary for word_id to doc_id mapping."""
    return defaultdict(default_doc_dict)


def process_chunk(chunk):
    """
    Process a chunk of the forward index to build a partial backward index.
    """
    partial_backward_index = defaultdict(default_word_dict)

    for doc_id, data in chunk.items():
        words = data["words"]  
        tf = data["tf"]  

        for word_id, position in words:
            partial_backward_index[word_id][doc_id]["positions"].append(position)
            partial_backward_index[word_id][doc_id]["tf"] = tf[word_id]

    return partial_backward_index


class BackwardIndex:
    def __init__(self, forward_index_file="indexes/forwardindex.pkl", output_file="indexes/backwardindex.pkl"):
        self.forward_index_file = forward_index_file
        self.output_file = output_file
        self.forward_index = None
        self.backward_index = defaultdict(default_word_dict)

    def load_forward_index(self):
        """Load the forward index from the pickle file."""
        with open(self.forward_index_file, "rb") as f:
            self.forward_index = pickle.load(f)

    def merge_backward_indexes(self, indexes):
        """
        Merge partial backward indexes into a single backward index.
        """
        for partial_index in indexes:
            for word_id, doc_data in partial_index.items():

                if word_id not in self.backward_index:
                    self.backward_index[word_id] = default_word_dict()

                for doc_id, details in doc_data.items():

                    if doc_id not in self.backward_index[word_id]:

                        self.backward_index[word_id][doc_id] = default_doc_dict()

                    self.backward_index[word_id][doc_id]["positions"].extend(details["positions"])
                    self.backward_index[word_id][doc_id]["tf"] += details["tf"]
        self.backward_index = dict(sorted(self.backward_index.items()))

    def create_backward_index(self, chunk_size=1000):
        self.load_forward_index()
        forward_index_items = list(self.forward_index.items())
        chunks = [
            dict(forward_index_items[i : i + chunk_size])
            for i in range(0, len(forward_index_items), chunk_size)
        ]
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
            backward_indexes = [future.result() for future in futures]

        self.merge_backward_indexes(backward_indexes)

        self.save_backward_index()

    def save_backward_index(self):
        """Save the backward index to a pickle file."""
        with open(self.output_file, "wb") as f:
            pickle.dump(self.backward_index, f)
        print(f"Backward index created and saved to {self.output_file}.")

    def load_backward_index(self):
        """Load the backward index from a pickle file."""
        with open(self.output_file, "rb") as f:
            self.backward_index = pickle.load(f)
        print("Backward index loaded successfully.")

    def print_backward_index(self):
        """Print the backward index contents."""
        for word_id, doc_data in self.backward_index.items():
            print(f"Word ID: {word_id}")
            for doc_id, details in doc_data.items():
                print(f"\tDocument ID: {doc_id}")
                print(f"\t\tPositions: {details['positions']}")
                print(f"\t\tTerm Frequency (TF): {details['tf']}")
            print("-" * 40)  


if __name__ == "__main__":

    backward_indexer = BackwardIndex()
    
    # Create the backward index from forward index
    backward_indexer.create_backward_index()

    # Optionally load and print the backward index
    # backward_indexer.load_backward_index()
    # backward_indexer.print_backward_index()
