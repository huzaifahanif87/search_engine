


import nltk
from nltk.corpus import stopwords
from rapidfuzz import fuzz, process
import itertools

class QueryProcessor:
    def __init__(self, lexicon):
        self.lexicon = lexicon
        nltk.download("stopwords")
        self.stop_words = set(stopwords.words("english"))

    def filter_stop_words(self, query_terms):
        """Filter out stop words from a list of query terms."""
        return [term for term in query_terms if term.lower() not in self.stop_words]

    def approximate_matches(self, term, threshold=80):
        """Find approximate matches for a term in the lexicon using fuzzy matching."""
        all_words = list(self.lexicon.get_all_words())  # Ensure words are in a list
        matches = process.extract(term, all_words, scorer=fuzz.ratio, limit=5)  # Limit to top 5 matches
        return [match[0] for match in matches if match[1] >= threshold]  # Use match[0] (word) and match[1] (score)


    def generate_combinations(self, term, max_combinations=500):
        """Generate character combinations for a term, with a limit for performance."""
        combinations = set()
        for length in range(1, len(term) + 1):
            combinations.update("".join(c) for c in itertools.combinations(term, length))
            if len(combinations) > max_combinations:
                break  # Limit the number of combinations for performance
        return combinations

    def process_query(self, query):
        """Process a query: filter stop words, match terms, and handle approximate matches."""
        query_terms = query.strip().split()

        # Remove stop words
        filtered_terms = self.filter_stop_words(query_terms)
        if not filtered_terms:
            filtered_terms = query_terms  # If only stop words are left, keep them

        query_term_ids = []
        for term in filtered_terms:
            term_id = self.lexicon.get_index(term)
            if term_id is not None:
                query_term_ids.append(term_id)
            else:
                # Attempt approximate matches
                approx_matches = self.approximate_matches(term)
                if approx_matches:
                    print(f"Approximate matches for '{term}': {approx_matches}")
                    query_term_ids.extend(self.lexicon.get_index(match) for match in approx_matches if self.lexicon.get_index(match))
                else:
                    # Generate combinations as a last resort
                    char_combinations = self.generate_combinations(term)
                    query_term_ids.extend(self.lexicon.get_index(comb) for comb in char_combinations if self.lexicon.get_index(comb))

        # Return term IDs and status
        if query_term_ids:
            return query_term_ids, "processed"
        else:
            return [], "no_matches"
