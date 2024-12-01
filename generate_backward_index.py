import pickle
from collections import defaultdict

def create_backward_index(forward_index_file="indexes/forward_index.pkl", output_file="indexes/backward_index.pkl"):

    with open(forward_index_file, "rb") as f:
        forward_index = pickle.load(f)
    
    backward_index = defaultdict(set)

    for doc_id, word_ids in forward_index.items():
        for word_id in word_ids:
            backward_index[word_id].add(doc_id)
    
    with open(output_file, "wb") as f:
        pickle.dump(backward_index, f)
    
    print(f"Backward index created and saved to {output_file}.")


if __name__ == "__main__":
    create_backward_index()