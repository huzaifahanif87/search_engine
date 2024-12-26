from concurrent.futures import ProcessPoolExecutor
from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy
from BackwardIndexBarrelizer import BackwardIndexBarrelizer
from DoumentDataGenerator import DocumentID
from query_processor import QueryProcessor
from Lexicon import *
from RankingSystem import RankingSystem
from ForwardIndex import ForwardIndex

from BackwardIndex import BackwardIndex
import os
import math
import time
import json
from concurrent.futures import ThreadPoolExecutor
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Thread pool for handling background tasks
executor = ThreadPoolExecutor(max_workers=3)
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return super(CustomJSONEncoder, self).default(obj)

app = Flask(__name__)


app.json_encoder = CustomJSONEncoder

lexicon = Lexicon("data/lexicon.txt")
lexicon.load_from_file()

query_processor = QueryProcessor(lexicon)
ranker = RankingSystem("backward_barrels", lexicon, "data/documents_data.pkl")


@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '').strip()
    page = int(request.json.get('page', 1))  
    results_per_page = 20  

    if not query:
        return jsonify({'status': 'no_query', 'message': 'Please provide a search term.'})


    query_term_ids, status = query_processor.process_query(query)
    if status == 'no_matches':
        return jsonify({'status': 'no_matches', 'message': 'No matches found.', 'query_status': 'No exact matches found, checking for related data...'})


    ranked_doc_ids = ranker.rank_documents(query_term_ids)
    total_results = len(ranked_doc_ids)


    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page
    paginated_doc_ids = ranked_doc_ids[start_index:end_index]

    results = []
    for doc_id in paginated_doc_ids:  
        document_data = ranker.get_document_data(doc_id)

        title = document_data.get('title', '')
        description = document_data.get('description', 'No description available')
        url = document_data.get('url', '')
        image_url = document_data.get('url_to_image', '')

        if not image_url or (isinstance(image_url, float) and math.isnan(image_url)):
            image_url = None

        source = document_data.get('source_name', '')

        results.append({
            'doc_id': doc_id,
            'details': {
                'title': title,
                'description': description,
                'url': url,
                'image_url': image_url,
                'source': source,
            }
        })

    total_pages = (total_results + results_per_page - 1) // results_per_page  

    return jsonify({
        'status': 'success',
        'results': results,
        'query_status': 'Exact matches found.',
        'total_pages': total_pages,
        'current_page': page
    })

@app.route('/update_data', methods=['POST'])
def update_data():
    """Handle CSV file upload, process it, and update the lexicon and indices."""
    try:
        if 'csv_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'})

        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'})

        if file and file.filename.endswith('.csv'):
            # Save the uploaded file temporarily
            csv_path = os.path.join('uploads', file.filename)
            file.save(csv_path)
            logging.info("CSV file uploaded successfully: %s", csv_path)

            # Submit update task to the thread pool
            future = executor.submit(process_update_task, csv_path)
            return jsonify({'status': 'success', 'message': 'Update process started in the background. Check logs for progress.'})

        return jsonify({'status': 'error', 'message': 'Invalid file format'})
    except Exception as e:
        logging.error("Error in update_data: %s", str(e))
        return jsonify({'status': 'error', 'message': str(e)})

# def process_update_task(csv_path):
#     """Background task to process updates."""
#     try:
#         logging.info("Starting update process...")

#         # Step 1: Update lexicon
#         update_lexicon(csv_path, lexicon)
#         lexicon.load_from_file()
#         logging.info("Lexicon updated successfully.")

#         # Step 2: Update forward index
#         forward_index = ForwardIndex("data/sampleData.csv", lexicon, "indexes/forwardindex.pkl")
#         last_doc_id_before = forward_index._get_last_document_id()
#         logging.info("Last document ID before update: %d", last_doc_id_before)
        
#         forward_index.update_forward_index()
#         logging.info("Forward index updated successfully.")

#         # Step 3: Determine updated document IDs
#         last_doc_id_now = forward_index._get_last_document_id()
#         logging.info("Last document ID after update: %d", last_doc_id_now)

#         updated_doc_ids = list(range(last_doc_id_before + 1, last_doc_id_now + 1)) if last_doc_id_now > last_doc_id_before else []
#         logging.info("Updated document IDs: %s", updated_doc_ids)

#         updated_word_ids = forward_index.get_unique_word_ids(updated_doc_ids)
#         logging.info("Updated word IDs: %s", updated_word_ids)

#         # Step 4: Update backward index
#         backward_index = BackwardIndex()
#         backward_index.update_backward_index(updated_doc_ids)
#         logging.info("Backward index updated successfully.")

#         # Step 5: Update backward index barrels
#         barrelizer = BackwardIndexBarrelizer()
#         barrelizer.update_barrels(updated_word_ids)
#         logging.info("Backward index barrels updated successfully.")

#         # Step 6: Update document data
#         document_id_instance = DocumentID(
#             document_file=csv_path,
#             output_file="data/documents_data.pkl"
#         )
#         document_id_instance.update_document_data()
#         logging.info("Document data updated successfully.")


#         logging.info("Update process completed successfully.")
#     except Exception as e:
#         logging.error("Error during update process: %s", str(e))

def process_update_task(csv_path):
    """Background task to process updates."""
    global query_processor, ranker  # Ensure we can update these objects globally
    try:
        logging.info("Starting update process...")

        # Step 1: Update lexicon
        update_lexicon(csv_path, lexicon)
        lexicon.load_from_file()
        logging.info("Lexicon updated successfully.")

        # Step 2: Update forward index
        forward_index = ForwardIndex("data/sampleData.csv", lexicon, "indexes/forwardindex.pkl")
        last_doc_id_before = forward_index._get_last_document_id()
        logging.info("Last document ID before update: %d", last_doc_id_before)
        
        forward_index.update_forward_index()
        logging.info("Forward index updated successfully.")

        # Step 3: Determine updated document IDs
        last_doc_id_now = forward_index._get_last_document_id()
        logging.info("Last document ID after update: %d", last_doc_id_now)

        updated_doc_ids = list(range(last_doc_id_before + 1, last_doc_id_now + 1)) if last_doc_id_now > last_doc_id_before else []
        logging.info("Updated document IDs: %s", updated_doc_ids)

        updated_word_ids = forward_index.get_unique_word_ids(updated_doc_ids)
        logging.info("Updated word IDs: %s", updated_word_ids)

        # Step 4: Update backward index
        backward_index = BackwardIndex()
        backward_index.update_backward_index(updated_doc_ids)
        logging.info("Backward index updated successfully.")

        # Step 5: Update backward index barrels
        barrelizer = BackwardIndexBarrelizer()
        barrelizer.update_barrels(updated_word_ids)
        logging.info("Backward index barrels updated successfully.")

        # Step 6: Update document data
        document_id_instance = DocumentID(
            document_file=csv_path,
            output_file="data/documents_data.pkl"
        )
        document_id_instance.update_document_data()
        logging.info("Document data updated successfully.")

        # Step 7: Reinitialize QueryProcessor and RankingSystem
        query_processor = QueryProcessor(lexicon)
        ranker = RankingSystem("backward_barrels", lexicon, "data/documents_data.pkl")
        logging.info("QueryProcessor and RankingSystem updated successfully.")

        logging.info("Update process completed successfully.")
    except Exception as e:
        logging.error("Error during update process: %s", str(e))


@app.route('/update')
def update():
    return render_template('update.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)





