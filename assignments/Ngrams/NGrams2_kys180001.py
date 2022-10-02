from nltk import word_tokenize
from nltk.util import ngrams
import pickle

languages = ['English', 'French', 'Italian']


# Load test file
def load_test():
    with open('ngram_files/ngram_files/LangId.test') as f:
        lines = f.readlines()
    return lines


# Calculate the probability that a sentence belongs to a particular language
def calc_probs(my_dict, test_bigrams, vocab_size):
    prob = 1
    uni_dict, bi_dict = my_dict
    for bigram in test_bigrams:
        unigram = (bigram[0],)  # Properly format unigram to find in unigram dictionary
        bi_count = bi_dict[bigram]  # Bigram count
        uni_count = uni_dict[unigram]   # Unigram count
        prob = prob * ((1 + bi_count) / (uni_count + vocab_size))   # Laplace smoothing
    return prob


# Make the predictions (classifications)
def make_class(dicts):
    classifications = []
    sentences = load_test()
    vocab_size = sum(list(dicts[0][0].values())) + sum(list(dicts[1][0].values())) + sum(list(dicts[2][0].values()))
    with open('Predictions.txt', 'w') as f:
        for sentence in sentences:
            probs = []
            tokens = word_tokenize(sentence)
            test_bigrams = list(ngrams(tokens, 2))
            for my_dict in dicts:
                probs.append(calc_probs(my_dict, test_bigrams, vocab_size))
            max_index = probs.index(max(probs))
            classifications.append(languages[max_index])
            f.write(languages[max_index] + '\n')
    return classifications


# Load the file containing the solutions
def load_sol():
    with open('ngram_files/ngram_files/LangId.sol') as f:
        lines = f.readlines()
    return lines


# Check the accuracy of predictions against the solution file
def check_accuracy(classifications):
    num_right, total = 0, len(classifications)
    actual_classes = load_sol()
    wrong = []
    for i, pair in enumerate(actual_classes):
        actual_class = pair.split()[1]
        if actual_class == classifications[i]:
            num_right += 1
        else:
            wrong.append(pair.split()[0])
    return num_right / total, wrong


# Load the dictionaries from the .pickle files
def get_dicts():
    train_path = 'LangId_train'
    en_train, fr_train, it_train = train_path + '_English', train_path + '_French', train_path + '_Italian'

    path_names = [en_train, fr_train, it_train]
    dicts = []
    for path in path_names:
        unigram = get_dict(path + '_unigram.pickle')
        bigram = get_dict(path + '_bigram.pickle')
        dicts.append((unigram, bigram))
    return dicts


# Get an individual dict given a path to a pickle file
def get_dict(path):
    with open(path, 'rb') as p:
        pickle_dict = pickle.load(p)
    return pickle_dict


# Enclosing function for the whole program
def main():
    dicts = get_dicts()
    classifications = make_class(dicts)
    accuracy, wrong = check_accuracy(classifications)
    print('Predictions: ', classifications)
    print('Accuracy: ', accuracy)
    print('Incorrect Predictions: ', wrong)


# If the program is being run as the main file, call main() to begin execution
if __name__ == '__main__':
    main()
