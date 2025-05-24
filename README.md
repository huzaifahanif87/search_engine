# Search Engine

Khoj is a scalable, modular Python-based search engine. It includes a full indexing pipeline (forward and backward indexes), dynamic document updates, TF-IDF computation, advanced query processing with fuzzy/compound matching, and a web UI for search and data management.

---

## Table of Contents

- [Project Architecture](#project-architecture)
- [Technologies Used](#technologies-used)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Core Modules Overview](#core-modules-overview)
- [Updating Data](#updating-data)
- [Notes](#notes)
- [Contributing](#contributing)
- [License](#license)

---

## Project Architecture

**Main Flow:**
1. **Data Ingestion:** Documents are loaded from CSV, parsed, and indexed.
2. **Lexicon:** Maintains mapping between unique words and their IDs, including stop word management.
3. **Forward Index:** Maps documents to word occurrences (with positions, term frequencies).
4. **Backward Index:** Maps words back to the documents they appear in (with positions, TF).
5. **Barrelization:** Indexes are split into "barrels" (chunks) for scalability.
6. **TF-IDF Computation:** Both index types store TF-IDF scores.
7. **Ranking System:** Ranks documents matching query terms using TF-IDF, proximity, and source credibility.
8. **Query Processor:** Handles user queries, fuzzy/approximate/compound/prefix matching, stop word filtering.
9. **Flask Web App:** Provides search & update endpoints and HTML UI.

---

## Technologies Used

- **Python 3.8+**
- **Flask** (web server and API)
- **spaCy** (tokenization, lemmatization)
- **NLTK** (stopwords)
- **RapidFuzz** (fuzzy/approximate string matching)
- **pandas** (CSV reading)
- **pickle** (efficient storage of indexes/data)
- **concurrent.futures** (parallelism for indexing)
- **Jinja2** (HTML templates, via Flask)

---

## Installation & Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/huzaifahanif87/search_engine.git
   cd search_engine
   ```

2. **Install dependencies:**
   ```sh
   pip install flask pandas spacy nltk rapidfuzz

   ```


3. **Download spaCy model:**
   ```sh
   python -m spacy download en_core_web_sm
   ```

4. **Prepare initial data:**
   - Place your CSV(s) in the `data/` directory (e.g., `sampleData.csv`).
   - Ensure `data/lexicon.txt` exists incase not, run lexicon.oy to create.
   - Create the following directories if not present: `indexes/`, `backward_barrels/`, `uploads/`. And create forward and bakwad indexes and barrels using their respective files.

---

## Usage

### Starting the Web Application

```sh
python app.py
```
- The app will run at `http://localhost:5000/`
- Use the web UI to search documents, or POST to `/search` with JSON: `{"query": "...", "page": 1}`.

### Updating Data

- Visit `/update` in the web UI, or POST a CSV file to `/update_data`.
- The update process (background thread) will:
  - Update the lexicon with new words.
  - Rebuild and append to the forward and backward indexes.
  - Update barrels and document data.
  - Hot-reload the in-memory QueryProcessor and RankingSystem.

---

## Core Modules Overview

### app.py
- **Flask application**.
- Handles routes for `/`, `/search`, `/update`, `/update_data`.
- Coordinates background data update jobs.
- Initializes shared objects (Lexicon, QueryProcessor, RankingSystem).

### Lexicon.py
- Manages word-to-ID mapping, stop words, and persistent lexicon storage.
- Supports fast loading/saving and parallel updates from CSV.

### ForwardIndex.py / ForwardIndexBarrelizer.py
- **ForwardIndex:** Maps doc_id → word occurrences, positions, TF.
- Supports chunked/parallel processing for large datasets.
- **Barrelizer:** Splits the index into "barrels" for scale; computes TF-IDF per doc.

### BackwardIndex.py / BackwardIndexBarrelizer.py
- **BackwardIndex:** Maps word_id → doc_ids, positions, TF.
- Can update only for new/changed documents.
- **Barrelizer:** Splits backward index into barrels; computes TF-IDF for word/doc pairs.

### DoumentDataGenerator.py
- Maintains a mapping of doc_id → metadata (title, url, source, etc.), synchronizing new documents from uploaded CSVs.

### Dynamic.py
- Utility for dynamically adding new documents to all indexes and barrels.

### query_processor.py
- Handles user queries:
  - Lowercasing, stop word removal.
  - Fuzzy and prefix matches (RapidFuzz).
  - Compound term splitting and character normalization.
  - Returns relevant word IDs for ranking.

### RankingSystem.py
- Ranks docs for a query using:
  - TF-IDF of matched terms.
  - Proximity of query terms within documents.
  - Source credibility (predefined trusted sources).
- Returns doc_id, metadata, and relevance scores.

---

## Updating Data

- **/update_data** endpoint allows uploading a new CSV for incremental ingestion.
- Lexicon and all indexes are updated in a background thread.
- New barrels are created as needed.
- Document data is merged with new entries.
- The app supports live updating without restart.

---

## Notes

- **Important:** `app.py` and all index/barrel classes assume existence of certain files; ensure initial CSVs are present.

---

