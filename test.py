# import pickle
# import os


# def load_backward_barrel(barrel_id, barrel_dir="backward_barrels"):
#     """Load a specific backward barrel."""
#     barrel_file = os.path.join(barrel_dir, f"backward_barrel_{barrel_id}.pkl")
#     if os.path.exists(barrel_file):
#         with open(barrel_file, "rb") as f:
#             return pickle.load(f)
#     else:
#         print(f"Backward barrel {barrel_id} does not exist.")
#         return None


# def print_specific_entry(barrel_data, entry_number):
#     """Print a specific entry in the backward barrel."""
#     for index, (word_id, doc_data) in enumerate(barrel_data.items()):
#         if index == entry_number:
#             print(f"Entry {entry_number} (Word ID: {word_id}):")
#             for doc_id, details in doc_data.items():
#                 print(f"\tDocument ID: {doc_id}")
#                 print(f"\t\tPositions: {details['positions']}")
#                 print(f"\t\tTerm Frequency (TF): {details['tf']}")
#                 if 'tfidf' in details:
#                     print(f"\t\tTF-IDF: {details['tfidf']}")
#             print("-" * 40)
#             return
#     print(f"Entry {entry_number} does not exist in the barrel.")


# def search_word_in_barrel(barrel_data, word_id):
    
#     """Search for a specific word in the backward barrel."""
#     if word_id in barrel_data:
#         print(f"Word ID: {word_id} found in the barrel:")
#         doc_data = barrel_data[word_id]
#         for doc_id, details in doc_data.items():
#             print(f"\tDocument ID: {doc_id}")
#             print(f"\t\tPositions: {details['positions']}")
#             print(f"\t\tTerm Frequency (TF): {details['tf']}")
#             if 'tfidf' in details:
#                 print(f"\t\tTF-IDF: {details['tfidf']}")
#         print("-" * 40)
#     else:
#         print(f"Word ID: {word_id} not found in the barrel.")


# def get_barrel_size(barrel_data):
#     """Get the number of entries in the backward barrel."""
#     return len(barrel_data)


# if __name__ == "__main__":
#     # Load the specific backward barrel
#     barrel_id = 2  # You can change this to load other barrels
#     barrel_data = load_backward_barrel(barrel_id)

#     if barrel_data:
#         # Display the size of the barrel
#         barrel_size = get_barrel_size(barrel_data)
#         print(f"Size of Barrel {barrel_id}: {barrel_size} entries")

#         # Display a specific entry (adjust for 0-based indexing)
#         entry_number = 4000
#         print_specific_entry(barrel_data, entry_number)

#         # Search for a specific word ID
#         word_id_to_search = 52121  # Replace with the actual word ID you want to search for
#         search_word_in_barrel(barrel_data, word_id_to_search)


import pickle

def load_forward_index(forward_index_file="indexes/forwardindex.pkl"):
    """Load the forward index from the pickle file."""
    with open(forward_index_file, "rb") as f:
        forward_index = pickle.load(f)
    return forward_index
def print_single_entry(forward_index, document_id=None):

    if document_id is None:
        # Get a random entry if no specific document ID is provided
        document_id, doc_data = next(iter(forward_index.items()))
        print(f"Printing a random entry (Document ID: {document_id}):")
    else:
        # Fetch the specific document if the ID exists
        doc_data = forward_index.get(document_id)
        if not doc_data:
            print(f"Document ID {document_id} not found in the forward index.")
            return
        print(f"Printing entry for Document ID: {document_id}")
    
    # Print the document data
    print(f"Document Data: {doc_data}")

def print_forward_index_size(forward_index):
    """Print the total size of the forward index."""
    total_documents = len(forward_index)
    total_words = sum(len(doc_data["words"]) for doc_data in forward_index.values())
    total_unique_words = len(set(word_id for doc_data in forward_index.values() for word_id, _ in doc_data["words"]))
    
    print(f"Total Documents: {total_documents}")
    print(f"Total Words (including duplicates): {total_words}")
    print(f"Total Unique Words: {total_unique_words}")

if __name__ == "__main__":
    forward_index_file = "indexes/forwardindex.pkl"  # Path to the forward index file
    forward_index = load_forward_index(forward_index_file)
    print_forward_index_size(forward_index)
    print_single_entry(forward_index)



# import pickle
# from collections import defaultdict


# class BackwardIndex:
#     def __init__(self, output_file="indexes/backwardindex.pkl"):
#         self.output_file = output_file
#         self.backward_index = defaultdict(self.default_word_dict)

#     def default_doc_dict(self):
#         """Default dictionary structure for backward index."""
#         return {"positions": [], "tf": 0}

#     def default_word_dict(self):
#         """Default dictionary for word_id to doc_id mapping."""
#         return defaultdict(self.default_doc_dict)

#     def load_backward_index(self):
#         """Load the backward index from a pickle file."""
#         with open(self.output_file, "rb") as f:
#             self.backward_index = pickle.load(f)
#         print("Backward index loaded successfully.")

#     def print_backward_index_size(self):
#         """Print the size of the backward index."""
#         num_word_ids = len(self.backward_index)
#         num_doc_entries = sum(len(doc_data) for doc_data in self.backward_index.values())
#         print(f"Backward index contains {num_word_ids} unique Word IDs.")
#         print(f"Backward index maps to {num_doc_entries} total Document entries.")

#     def print_specific_word(self, word_id):
#         """Print details for a specific word ID."""
#         if word_id in self.backward_index:
#             print(f"Word ID: {word_id}")
#             for doc_id, details in self.backward_index[word_id].items():
#                 print(f"\tDocument ID: {doc_id}")
#                 print(f"\t\tPositions: {details['positions']}")
#                 print(f"\t\tTerm Frequency (TF): {details['tf']}")
#             print("-" * 40)
#         else:
#             print(f"Word ID {word_id} not found in the backward index.")

#     def print_entry(self, entry_number):
#         """Print the details of a specific entry in the backward index."""
#         for index, (word_id, doc_data) in enumerate(self.backward_index.items()):
#             if index == entry_number:
#                 print(f"Entry {entry_number} (Word ID: {word_id}):")
#                 for doc_id, details in doc_data.items():
#                     print(f"\tDocument ID: {doc_id}")
#                     print(f"\t\tPositions: {details['positions']}")
#                     print(f"\t\tTerm Frequency (TF): {details['tf']}")
#                 print("-" * 40)
#                 return
#         print(f"Entry {entry_number} does not exist in the backward index.")

#     def print_backward_index(self, max_entries=1):
#         """Print the first few entries of the backward index."""
#         print(f"Printing the first {max_entries} entries in the backward index:")
#         for i, (word_id, doc_data) in enumerate(self.backward_index.items()):
#             if i >= max_entries:
#                 break
#             print(f"Word ID: {word_id}")
#             for doc_id, details in doc_data.items():
#                 print(f"\tDocument ID: {doc_id}")
#                 print(f"\t\tPositions: {details['positions']}")
#                 print(f"\t\tTerm Frequency (TF): {details['tf']}")
#             print("-" * 40)


# if __name__ == "__main__":
#     # Create a BackwardIndex instance
#     backward_indexer = BackwardIndex()

#     # Load the backward index from the pickle file
#     backward_indexer.load_backward_index()

#     # Print the size of the backward index
#     backward_indexer.print_backward_index_size()

#     # Print the first few entries (limit to 10 entries for readability)
#     backward_indexer.print_backward_index(max_entries=1)

#     # Optionally, print a specific word ID
#     word_id = int(input("\nEnter a Word ID to inspect: ").strip())
#     backward_indexer.print_specific_word(word_id)

#     # Optionally, print a specific entry by its number
#     entry_number = int(input("\nEnter an entry number to inspect: ").strip())
#     backward_indexer.print_entry(entry_number)
