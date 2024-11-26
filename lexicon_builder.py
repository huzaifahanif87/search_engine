    
from lexicon import Lexicon
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os    



# for processig csv to lexicon:
def process_csv_to_lexicon(csv_file, lexicon, columns):
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(csv_file, encoding="ISO-8859-1")

        # Tokenize words from the specified columns
        for column in columns:
            if column not in df.columns:
                print(f"Column '{column}' not found in the CSV. Skipping...")
                continue

            for text in df[column]:
                if isinstance(text, str):  # taking strings only atm
                    words = word_tokenize(text.lower())
                    words = [
                        word
                        for word in words
                        if word.isalpha() and word not in stopwords.words("english") # using python library to avoid taking extra words. will ceate a separate file for them
                    ]
                    for word in words:
                        lexicon.add_word(word)

    except UnicodeDecodeError:
        print("Unicode decode error. Try using a different encoding like 'ISO-8859-1'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
  # update with whatever path u have. and put it in project folder to avoid xtra git push. first try with small sample that i am cuurently uploading for ease
    csv_file = r"data/sampleData.csv"

    columns_to_process = ["full_content", "content"]   # adding both of these because personally cheked it made difference
    lexicon = Lexicon()


    process_csv_to_lexicon(csv_file, lexicon, columns_to_process)


    lexicon.save_to_file()

    print("Lexicon created and saved successfully!")
