
import pandas as pd
import pickle
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from lexicon import Lexicon  

# only for first time
# import nltk
# nltk.download('punkt')
# nltk.download('stopwords')

def create_forward_index(csv_file, lexicon_file="data/lexicon.txt", output_file="indexes/forward_index.pkl"):
    """
    Generate a forward index mapping document IDs to word IDs from specified columns.
    """
    lexicon = Lexicon(lexicon_file)
    
    # Load the existing lexicon
    lexicon.load_from_file()
    
    forward_index = {}
    df = pd.read_csv(csv_file, encoding="ISO-8859-1")

    # Columns to process
    columns_to_process = ["content", "full_content"]

    for doc_id, row in df.iterrows():
        forward_index[doc_id] = []

        for column in columns_to_process:
            if column in df.columns:
                text = row[column]
                if isinstance(text, str):  # Ensure the column contains a string
                    words = word_tokenize(text.lower())
                    words = [word for word in words if word.isalpha() and word not in stopwords.words("english")]

                    for word in words:
                        word_id = lexicon.get_index(word)
                        if word_id is not None:
                            forward_index[doc_id].append(word_id)

    # Save the forward index to a pickle file
    with open(output_file, "wb") as f:
        pickle.dump(forward_index, f)
    
    print(f"Forward index created and saved to {output_file}.")


if __name__ == "__main__":
    csv_file = r"data/sampleData.csv"  # Put whatever the correct path as needed
    create_forward_index(csv_file)
