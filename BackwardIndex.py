import pickle
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from ForwardIndex import default_forward_index  # Import the function from the ForwardIndex module
from concurrent.futures import ThreadPoolExecutor

def default_doc_dict():
    """Default dictionary structure for backward index."""
    return {"positions": [], "tf": 0}


def default_word_dict():
    """Default dictionary for word_id to doc_id mapping."""
    return defaultdict(default_doc_dict)


def process_chunk(chunk, updated_doc_ids):
    """
    Process a chunk of the forward index to build a partial backward index.
    Only updates the entries corresponding to the updated document IDs.
    """
    partial_backward_index = defaultdict(default_word_dict)

    for doc_id, data in chunk.items():
        if doc_id not in updated_doc_ids:
            continue  # Skip documents that haven't been updated

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

    def load_backward_index(self):
        """Load the backward index from a pickle file."""
        with open(self.output_file, "rb") as f:
            self.backward_index = pickle.load(f)
        print("Backward index loaded successfully.")

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

    def update_backward_index(self, updated_word_ids):
        """Update the backward index with the given updated document IDs."""
        self.load_forward_index() # Load the forward index
        self.load_backward_index()  # Load the existing backward index
        # Loop through the updated document IDs and update the backward index
        for doc_id in updated_doc_ids:
            # Check if the doc_id exists in the forward index
            if doc_id not in self.forward_index:
                print(f"Document ID {doc_id} not found in the forward index.")
                continue

            data = self.forward_index[doc_id]
            words = data["words"]  # List of (word_id, position) pairs
            tf = data["tf"]  # Term frequency for the words in this document

            # Update the backward index
            for word_id, position in words:
                # Check if word_id exists in the backward index, if not create it
                if word_id not in self.backward_index:
                    self.backward_index[word_id] = defaultdict(default_doc_dict)

                # Update the positions and term frequency (TF)
                self.backward_index[word_id][doc_id]["positions"].append(position)
                self.backward_index[word_id][doc_id]["tf"] = tf.get(word_id, 0)  # Ensure we use tf if available

        # Save the updated backward index
        self.save_backward_index()


    def save_backward_index(self):
        """Save the backward index to a pickle file."""
        with open(self.output_file, "wb") as f:
            pickle.dump(self.backward_index, f)
        print(f"Backward index updated and saved to {self.output_file}.")

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
    # Initialize the BackwardIndex
    backward_indexer = BackwardIndex()

    # List of document IDs that were updated in the forward index
    updated_doc_ids = [50001]  # Example: Document IDs that were updated

    # Update the backward index based on the updated forward index documents
    backward_indexer.update_backward_index(updated_doc_ids)

    # Optionally load and print the updated backward index
    # backward_indexer.load_backward_index()
    # backward_indexer.print_backward_index()
