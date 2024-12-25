from flask import Flask, render_template, request, jsonify
from query_processor import QueryProcessor
from Lexicon import Lexicon
from RankingSystem import RankingSystem
import math
import time
import json
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

if __name__ == '__main__':
    app.run(debug=True)
