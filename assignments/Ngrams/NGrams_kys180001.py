import collections
from nltk import word_tokenize
from nltk.util import ngrams
import os
import pickle


# Class that provides functionality for formatting data and loading data
class LangDataSet:
    # Constructor
    def __init__(self):
        self.raw_text = None

    # Load the data as raw text while stripping the raw text of newlines.
    def load_data(self, path):
        print(path)
        with open(path, 'r', encoding='latin1') as f:
            self.raw_text = f.read()
        self.raw_text = ''.join(self.raw_text.split('\n'))

    # Tokenize the raw_text using word_tokenize
    def tokenize(self):
        return word_tokenize(self.raw_text)

    # Return the list of bigrams of the tokenized text
    def bigrams(self):
        return list(ngrams(self.tokenize(), 2))

    # Return the list of unigrams of the tokenized text
    def unigrams(self):
        return list(ngrams(self.tokenize(), 1))


# Preprocessing function that gets the relevant views of the raw text for a given language
def preprocess(language):
    base_path = 'ngram_files/ngram_files'
    dataset = LangDataSet()

    dataset.load_data(os.path.join(base_path, language))

    # Load bigrams and unigrams
    lang_bigrams = dataset.bigrams()
    lang_unigrams = dataset.unigrams()

    # Get counts of bigrams and unigrams the "Pythonic" way using the collections.Counter
    lang_bi_counts = collections.Counter(lang_bigrams)
    lang_uni_counts = collections.Counter(lang_unigrams)

    # Return the dictionaries containing the counts of each unigram and bigram
    return lang_uni_counts, lang_bi_counts


# Enclosing function for the whole program
def main():
    # Create paths to each language file
    train_path = 'LangId.train'
    en_train, fr_train, it_train = train_path + '.English', train_path + '.French', train_path + '.Italian'

    path_names = [en_train, fr_train, it_train]  # Create a list of language file names to iterate through
    datasets = []   # List of datasets (organized as a tuple, each tuple corresponding to a language)

    # Get the datasets
    for path_name in path_names:
        datasets.append(preprocess(path_name))

    # datasets[i][0] contains the unigrams, datasets[i][1] contains the bigrams
    for i, dataset in enumerate(datasets):
        with open(path_names[i].replace('.', '_') + '_unigram.pickle', 'wb') as p:
            pickle.dump(dataset[0], p, protocol=pickle.HIGHEST_PROTOCOL)
        with open(path_names[i].replace('.', '_') + '_bigram.pickle', 'wb') as p:
            pickle.dump(dataset[1], p, protocol=pickle.HIGHEST_PROTOCOL)


# If the program is being run as the main file, call main() to begin execution
if __name__ == '__main__':
    main()
