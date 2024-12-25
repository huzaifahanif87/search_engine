import pandas as pd
import pickle
from collections import defaultdict
from BackwardIndex import default_doc_dict
from BackwardIndexBarrelizer import BackwardIndexBarrelizer
from Lexicon import Lexicon
import spacy

def dynamic_update(new_csv_file, lexicon_file, forward_index_file, backward_index_file, barrel_dir):
    # Load existing data
    lexicon = Lexicon(lexicon_file)
    lexicon.load_from_file()

    with open(forward_index_file, "rb") as f:
        forward_index = pickle.load(f)

    with open(backward_index_file, "rb") as f:
        backward_index = pickle.load(f)

    # Process new document
    df = pd.read_csv(new_csv_file, encoding="ISO-8859-1")
    new_doc_id = max(forward_index.keys(), default=-1) + 1
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    column_weights = {"title": 4, "url": 3, "description": 2, "content": 1, "full_content": 1}

    new_forward_entry = {"words": [], "tf": defaultdict(int)}
    for _, row in df.iterrows():
        for col in column_weights:
            if pd.notna(row.get(col)):
                words = [token.lemma_ for token in nlp(row[col].lower()) if token.is_alpha]
                weight = column_weights[col]
                for pos, word in enumerate(words):
                    if word not in lexicon.words:
                        lexicon.add_words([word])
                    word_id = lexicon.get_index(word)
                    new_forward_entry["words"].append((word_id, pos))
                    new_forward_entry["tf"][word_id] += weight

    # Update forward index
    forward_index[new_doc_id] = new_forward_entry

    # Update backward index
    for word_id, count in new_forward_entry["tf"].items():
        if word_id not in backward_index:
            backward_index[word_id] = defaultdict(default_doc_dict)
        backward_index[word_id][new_doc_id] = {"positions": [], "tf": count}

    # Save updated data
    lexicon.save_to_file()
    with open(forward_index_file, "wb") as f:
        pickle.dump(forward_index, f)

    with open(backward_index_file, "wb") as f:
        pickle.dump(backward_index, f)

    # Update barrels
    barrelizer = BackwardIndexBarrelizer(backward_index_file=backward_index_file, output_dir=barrel_dir)
    barrelizer.create_barrels()
    print("Dynamic update completed!")


def main():
    # Hardcoded values for testing
    new_csv_file = "data/sampleData.csv"
    lexicon_file = "data/lexicon.txt"
    forward_index_file = "indexes/forwardindex.pkl"
    backward_index_file = "indexes/backwardindex.pkl"
    barrel_dir = "backward_barrels"

    # Run dynamic update
    try:
        dynamic_update(
            new_csv_file=new_csv_file,
            lexicon_file=lexicon_file,
            forward_index_file=forward_index_file,
            backward_index_file=backward_index_file,
            barrel_dir=barrel_dir,
        )
        print("Update process completed successfully.")
    except Exception as e:
        print(f"An error occurred during the update process: {e}")

if __name__ == "__main__":
    main()
