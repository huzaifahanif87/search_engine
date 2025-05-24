import pandas as pd
import pickle
import os

class DocumentID:
    def __init__(self, document_file="data/sfiftyData.csv", output_file="data/documents_data.pkl"):
        self.document_file = document_file
        self.output_file = output_file

    def load_existing_data(self):
        """Load existing document data from the pickle file."""
        if os.path.exists(self.output_file):
            with open(self.output_file, "rb") as f:
                return pickle.load(f)
        return {}

    def load_new_data(self):
        """Load new document data from the CSV file."""
        if not os.path.exists(self.document_file):
            raise FileNotFoundError(f"CSV file not found: {self.document_file}")

        df = pd.read_csv(self.document_file, encoding="ISO-8859-1")

        # Validate and filter documents with essential fields only
        valid_documents = []
        for _, row in df.iterrows():
            if not pd.isnull(row.get("url")):
                valid_documents.append({
                    "url": row.get("url", ""),
                    "url_to_image": row.get("url_to_image", ""),
                    "published_at": row.get("published_at", ""),
                    "source_name": row.get("source_name", ""),
                    "title": row.get("title", ""),
                    "description": row.get("description", ""),
                })
        return valid_documents

    def update_document_data(self):
        """Update the document data by appending new data and saving it back to the pickle file."""
        # Load existing and new data
        existing_data = self.load_existing_data()
        new_data = self.load_new_data()

        # Find the starting document ID for new data
        start_id = max(existing_data.keys(), default=-1) + 1

        # Append new data to the existing dictionary
        new_entries = {}
        for idx, document in enumerate(new_data):
            doc_id = start_id + idx
            new_entries[doc_id] = document

        if not new_entries:
            print("No valid new documents to add.")
            return

        # Combine existing and new data
        updated_data = {**existing_data, **new_entries}

        # Save the updated data back to the pickle file
        with open(self.output_file, "wb") as f:
            pickle.dump(updated_data, f)

        # Print the newly added documents
        print("Newly added documents:")
        for doc_id, document in new_entries.items():
            print(f"Document ID {doc_id}: {document}")

if __name__ == "__main__":
    document_id_instance = DocumentID(
        document_file="data/sfiftydata.csv", 
        output_file="data/documents_data.pkl"
    )

    # Update the document data
    document_id_instance.update_document_data()

      return self.documents_data.get(doc_id, None)


