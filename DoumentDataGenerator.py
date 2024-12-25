import pandas as pd
import pickle
import os

class DocumentID:
    def __init__(self, document_file="data/documents.csv", output_file="data/documents_data.pkl"):
        self.document_file = document_file
        self.output_file = output_file
        self.documents_data = {}  

    def load_from_csv(self):
        """Load document data (including title and description) from a CSV file and assign document IDs."""
        if not os.path.exists(self.document_file):
            raise FileNotFoundError(f"CSV file not found: {self.document_file}")


        df = pd.read_csv(self.document_file, encoding="ISO-8859-1")

        # Iterate through each row and assign a document ID
        for idx, row in df.iterrows():
            doc_data = {
                "url": row.get('url', ''),
                "url_to_image": row.get('url_to_image', ''),
                "published_at": row.get('published_at', ''),
                "source_name": row.get('source_name', ''),
                "title": row.get('title', ''),  
                "description": row.get('description', ''),  
            }
            self.documents_data[idx] = doc_data  # Assign document ID starting from 0

    def save_to_pickle(self):
        """Save the documents data to a pickle file."""
        with open(self.output_file, "wb") as f:
            pickle.dump(self.documents_data, f)
        print(f"Document data saved to {self.output_file}")

    def generate_document_data(self):
        """Generate the document data by loading from CSV and saving to pickle."""
        self.load_from_csv()
        self.save_to_pickle()

    def get_document_data(self, doc_id):
        """Get the details of a document by its ID."""
        return self.documents_data.get(doc_id, None)



if __name__ == "__main__":

    document_id_instance = DocumentID(document_file="data/sfiftydata.csv")  # Update whatever CSV path

    # Generate and save document data
    document_id_instance.generate_document_data()


    doc_id = 1  # only for testing
    doc_data = document_id_instance.get_document_data(doc_id)
    if doc_data:
        print(f"Document ID {doc_id} details: {doc_data}")
    else:
        print(f"Document ID {doc_id} not found.")
