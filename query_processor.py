
import nltk
from nltk.corpus import stopwords
from rapidfuzz import fuzz, process
import itertools
import re

class QueryProcessor:
    def __init__(self, lexicon):
        self.lexicon = lexicon
        nltk.download("stopwords")
        self.stop_words = set(stopwords.words("english"))

    def approximate_matches(self, term, threshold=85):
        """Find approximate matches for a term in the lexicon using fuzzy matching."""
        all_words = list(self.lexicon.get_all_words())  # Ensure words are in a list
        matches = process.extract(term, all_words, scorer=fuzz.ratio, limit=5)  # Limit to top 5 matches
        return [match[0] for match in matches if match[1] >= threshold]  # Use match[0] (word) and match[1] (score)

    def simplify_repeated_characters(self, term):
        """Simplify repeated characters to a base form, e.g., 'gazaaaaaaaaaaaa' -> 'gaza'."""
        return re.sub(r'(.)\1{2,}', r'\1', term)  # Replace three or more repeated characters with a single one

    # def split_compound_term(self, term):
    #     """Split compound terms like 'imrankhan' into 'imran' and 'khan'."""
    #     all_words = set(self.lexicon.get_all_words())  # Get all lexicon words

    #     # Prioritize finding the longest match first
    #     matches = []
    #     for i in range(1, len(term)):
    #         part1, part2 = term[:i], term[i:]
    #         if part1 in all_words and part2 in all_words:
    #             matches.append((part1, part2))

    #     # Instead of simply splitting, we now try matching "imra" with "imran"
    #     if not matches:
    #         possible_matches = [word for word in all_words if term in word]  # Find substrings in longer words
    #         matches.extend([(term, match) for match in possible_matches if term in match])

    #     return matches
    def split_compound_term(self, term):
        """Split compound terms into known lexicon words."""
        all_words = set(self.lexicon.get_all_words())  # Get all lexicon words
        matches = []

        # Try splitting the term at every possible position
        for i in range(1, len(term)):
            part1, part2 = term[:i], term[i:]
            
            # Check if both parts are valid words in the lexicon
            if part1 in all_words and part2 in all_words:
                matches.append((part1, part2))
        
        # If no exact match found, try for compound matches
        if not matches:
            for i in range(1, len(term)):
                part1 = term[:i]
                if part1 in all_words:
                    part2 = term[i:]
                    if part2 in all_words:  # Check if second part is also a word
                        matches.append((part1, part2))

        return matches

    def generate_combinations(self, term, max_combinations=500):
        """Generate character combinations for a term, with a limit for performance."""
        combinations = set()
        for length in range(1, len(term) + 1):
            combinations.update("".join(c) for c in itertools.combinations(term, length))
            if len(combinations) > max_combinations:
                break  # Limit the number of combinations for performance
        return combinations

    def filter_stop_words(self, query_terms):
        """Filter out stop words from a list of query terms, case-insensitively."""
        return [term for term in query_terms if term.lower() not in self.stop_words]

    def find_prefix_matches(self, term):
        """Find possible prefix matches for a term, considering its starting characters."""
        all_words = list(self.lexicon.get_all_words())
        return [word for word in all_words if word.startswith(term)]

    def process_query(self, query):
        """Process a query: handle compound terms, filter stop words, match terms, and handle approximate matches."""
        query_terms = query.strip().split()

        # Normalize query terms to lowercase
        normalized_terms = [term.lower() for term in query_terms]

        # Remove stop words
        filtered_terms = self.filter_stop_words(normalized_terms)
        if not filtered_terms:
            filtered_terms = normalized_terms  # If only stop words are left, keep them

        query_term_ids = []
        for term in filtered_terms:
            # Simplify repeated characters (e.g., 'gazaaaaaaaaaaaa' -> 'gaza')
            simplified_term = self.simplify_repeated_characters(term)

            # Try exact matching in lexicon first
            term_id = self.lexicon.get_index(simplified_term)  # Match simplified term
            if term_id is not None:
                query_term_ids.append(term_id)
            else:
                prefix_matches = self.find_prefix_matches(simplified_term)
                if prefix_matches:
                    print(f"Prefix matches for '{simplified_term}': {prefix_matches}")
                    query_term_ids.extend(self.lexicon.get_index(match) for match in prefix_matches if self.lexicon.get_index(match))

                # Handle compound terms (like "imrankhan" -> "imran" and "khan")
                compound_matches = self.split_compound_term(simplified_term)
                if compound_matches:
                    print(f"Compound matches for '{simplified_term}': {compound_matches}")
                    for part1, part2 in compound_matches:
                        term_id1 = self.lexicon.get_index(part1)
                        term_id2 = self.lexicon.get_index(part2)
                        if term_id1 is not None:
                            query_term_ids.append(term_id1)
                        if term_id2 is not None:
                            query_term_ids.append(term_id2)
                else:
                    # Attempt approximate matches as fallback
                    prefix_matches = self.find_prefix_matches(simplified_term)
                    if prefix_matches:
                        print(f"Prefix matches for '{simplified_term}': {prefix_matches}")
                        query_term_ids.extend(self.lexicon.get_index(match) for match in prefix_matches if self.lexicon.get_index(match))

                    approx_matches = self.approximate_matches(simplified_term)
                    if approx_matches:
                        print(f"Approximate matches for '{simplified_term}': {approx_matches}")
                        query_term_ids.extend(self.lexicon.get_index(match) for match in approx_matches if self.lexicon.get_index(match))

                    # If no matches found, check for prefix matches (for cases like "imra" to "imran")
                    # prefix_matches = self.find_prefix_matches(simplified_term)
                    # if prefix_matches:
                    #     print(f"Prefix matches for '{simplified_term}': {prefix_matches}")
                    #     query_term_ids.extend(self.lexicon.get_index(match) for match in prefix_matches if self.lexicon.get_index(match))

        # Return term IDs and status
        if query_term_ids:
            return query_term_ids, "processed"
        else:
            return [], "no_matches"
