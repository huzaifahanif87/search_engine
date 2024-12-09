import os
import pickle

class ForwardIndexBarrelizer:
    def __init__(self, forward_index_file="indexes/forward_index.pkl", output_dir="forward_barrels", docs_per_barrel=5000):
        self.forward_index_file = forward_index_file
        self.output_dir = output_dir
        self.docs_per_barrel = docs_per_barrel

        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load_forward_index(self):
        """Load the forward index from a pickle file."""
        with open(self.forward_index_file, "rb") as f:
            return pickle.load(f)

    def save_barrel(self, barrel_id, barrel_data):
        """Save a barrel to a pickle file."""
        barrel_file = os.path.join(self.output_dir, f"forward_barrel_{barrel_id}.pkl")
        with open(barrel_file, "wb") as f:
            pickle.dump(barrel_data, f)
        print(f"Forward barrel {barrel_id} saved.")

    def create_barrels(self):
        """Divide the forward index into barrels based on document IDs."""
        forward_index = self.load_forward_index()

        # Create barrels
        barrel_id = 0
        barrel_data = {}
        for doc_id, data in forward_index.items():
            barrel_data[doc_id] = data

            if len(barrel_data) >= self.docs_per_barrel:
                self.save_barrel(barrel_id, barrel_data)
                barrel_id += 1
                barrel_data = {}

        # Save the last barrel if it has remaining documents
        if barrel_data:
            self.save_barrel(barrel_id, barrel_data)

# Usage
if __name__ == "__main__":
    barrelizer = ForwardIndexBarrelizer()
    barrelizer.create_barrels()
