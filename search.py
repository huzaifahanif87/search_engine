from query_processor import QueryProcessor
from Lexicon import Lexicon
from RankingSystem import RankingSystem
import time


def main():
    # Path configurations
    backward_barrel_dir = "backward_barrels"
    documents_data_file = "data/documents_data.pkl"

    # Initialize and load the lexicon
    lexicon = Lexicon("data/lexicon.txt")
    try:
        lexicon.load_from_file()
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the lexicon file exists and the path is correct.")
        return

    # Initialize query processor and ranking system
    query_processor = QueryProcessor(lexicon)
    try:
        ranker = RankingSystem(backward_barrel_dir, lexicon, documents_data_file)
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure all required files and directories are set up correctly.")
        return
    print("Type 'exit' to quit the search.")

    while True:
        # Accept query input from the user
        query = input("\nEnter search query: ").strip()

        # Exit condition
        if query.lower() == "exit":
            print("Exiting the search. Goodbye!")
            break

        # Handle empty query
        if not query:
            print("Empty query. Please enter a valid search term.")
            continue

        # Start timer
        start_time = time.time()

        # Process the query
        query_term_ids, status = query_processor.process_query(query)

        if status == "no_matches":
            print("Looks like no great matches for your query. Try refining it!")
            continue

        # Rank documents based on the processed query
        try:
            ranked_doc_ids = ranker.rank_documents(query_term_ids)
        except Exception as e:
            print(f"An error occurred while processing the query: {e}")
            continue

        # End timer
        end_time = time.time()
        elapsed_time = end_time - start_time

if __name__ == "__main__":
    main()
