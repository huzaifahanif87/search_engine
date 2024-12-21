
import os
import pickle
import heapq


class RankingSystem:
    def __init__(self, backward_barrel_dir, lexicon, documents_data_file, words_per_barrel=5000):
        self.backward_barrel_dir = backward_barrel_dir
        self.lexicon = lexicon
        self.documents_data_file = documents_data_file
        self.words_per_barrel = words_per_barrel
        self.documents_data = self.load_documents_data()

        # Load each barrel into a separate dictionary
        self.barrels = self.load_all_barrels()

        # Set a fixed total number of documents
        self.total_docs = 50000

        # Define credibility scores for trusted sources
        self.source_credibility = {
            "wikipedia": 2,
            "bbc": 2,
            "nytimes": 1.5,
            "cnn": 1.5,
            # Add more sources as needed
        }

    def list_barrels(self, dir_path):
        """List all barrel files in a directory."""
        return sorted([f for f in os.listdir(dir_path) if f.endswith(".pkl")])

    def load_all_barrels(self):
        """Load all barrels into separate dictionaries."""
        barrel_files = self.list_barrels(self.backward_barrel_dir)
        barrels = {}

        for barrel_id, barrel_file in enumerate(barrel_files):
            barrel_path = os.path.join(self.backward_barrel_dir, barrel_file)
            with open(barrel_path, "rb") as f:
                barrels[barrel_id] = pickle.load(f)

        return barrels

    def load_documents_data(self):
        """Load document data (ID, details) from pickle file."""
        if not os.path.exists(self.documents_data_file):
            raise FileNotFoundError(f"Documents data file not found: {self.documents_data_file}")

        with open(self.documents_data_file, "rb") as f:
            return pickle.load(f)


    def rank_documents(self, query_term_ids):
        """Rank documents based on the query term IDs using multiple heaps for better prioritization."""
        # Dictionary to store heaps based on the number of query terms matched
        term_match_heaps = {i: [] for i in range(1, len(query_term_ids) + 1)}

        relevant_docs = {}

        # Collect document information
        for word_id in query_term_ids:
            for barrel_id, barrel_data in self.barrels.items():
                if word_id in barrel_data:
                    for doc_id, doc_info in barrel_data[word_id].items():
                        if doc_id not in relevant_docs:
                            relevant_docs[doc_id] = {
                                "tf_idf": 0,
                                "term_hits": set(),
                                "positions": []
                            }
                        relevant_docs[doc_id]["tf_idf"] += doc_info.get("tfidf", 0)
                        relevant_docs[doc_id]["term_hits"].add(word_id)
                        relevant_docs[doc_id]["positions"].append(doc_info["positions"])

        # Place documents into appropriate heaps
        for doc_id, data in relevant_docs.items():
            matched_terms = len(data["term_hits"])  # Number of query terms matched
            if matched_terms > 0:
                # Calculate proximity score
                proximity_score = self.calculate_proximity_score(query_term_ids, data["positions"])

                # Final score includes tf-idf and proximity
                score = data["tf_idf"] * proximity_score

                # Retrieve document details for source credibility
                doc_details = self.documents_data.get(doc_id, {})
                source_name = doc_details.get("source_name", "unknown")
                credibility_score = self.calculate_credibility_score(source_name)
                score += credibility_score

                # Push to the appropriate heap
                heapq.heappush(term_match_heaps[matched_terms], (-score, doc_id))

        # Combine heaps, prioritizing higher match counts
        ranked_docs = []
        for i in range(len(query_term_ids), 0, -1):  # Start from the heap with the most matches
            while term_match_heaps[i]:
                _, doc_id = heapq.heappop(term_match_heaps[i])
                ranked_docs.append(doc_id)

        return ranked_docs



    def calculate_proximity_score(self, query_term_ids, word_positions):
        """Calculate proximity score for query terms in a document."""
        if len(word_positions) <= 1:
            return 1  # Single-term queries or single occurrence

        # Find minimum distance between query term positions
        min_distance = float("inf")
        for i, pos_list1 in enumerate(word_positions):
            for j, pos_list2 in enumerate(word_positions):
                if i != j:
                    min_distance = min(min_distance, abs(min(pos_list1) - min(pos_list2)))

        return 1 / (1 + min_distance)  # Higher score for closer terms

    def calculate_credibility_score(self, source_name):
        """Get credibility score for a source."""
        source_name = source_name.lower()
        return self.source_credibility.get(source_name, 1)  # Default score is 1 for unknown sources

    def get_document_url(self, doc_id):
        """Retrieve document URL by its document ID."""
        return self.documents_data.get(doc_id, {}).get("url", "URL not found.")
    

    def get_document_details(self, doc_id):
        """Fetch and return document details by its ID."""
        doc_data = self.documents_data.get(doc_id)
        if not doc_data:
            return f"Document ID {doc_id} not found."
        return (
            f"Title: {doc_data.get('title', 'N/A')}\n"
            f"Description: {doc_data.get('description', 'N/A')}\n"
            f"Source: {doc_data.get('source_name', 'N/A')}\n"
            f"Published At: {doc_data.get('published_at', 'N/A')}\n"
            f"URL: {doc_data.get('url', 'N/A')}"
        )
    
    def get_document_data(self, doc_id):
        """Get the details of a document by its ID."""
        doc_data = self.documents_data.get(doc_id)
        if not doc_data:
            return None  # Ensure None is returned if the doc is not found
        return doc_data

