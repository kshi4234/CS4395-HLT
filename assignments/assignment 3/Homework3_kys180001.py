import collections
import sys
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from random import randint


# Function to open file and returns the raw text
def open_file():
    path = sys.argv[1]
    with open(path, 'r') as f:
        raw_text = f.read()
    return raw_text


# Function to calculate lexical diversity
def lexical_diversity(text):
    tokens = word_tokenize(text)  # Gets tokens
    u_tokens = set(tokens)  # Gets unique tokens
    return float(len(u_tokens)) / len(tokens)  # Make one element a float to ensure that division returns decimal


# Function to preprocess the text
def preprocess(text):
    tokens = word_tokenize(text)  # Gets the tokens
    # The below uses list comprehension to include the token if it is alphabetic, not in the stopwords,
    # and is longer than 5 characters.
    reduced = [t for t in tokens if t.isalpha() and t not in set(stopwords.words('english')) and len(t) > 5]

    lemmatizer = WordNetLemmatizer()  # Create the lemmatizer
    lemma = set([lemmatizer.lemmatize(w) for w in reduced])  # Unique lemmas of the lemmas in the reduced token list.

    tags = pos_tag(lemma)  # Gives POS tags to all lemmas
    print('First twenty tags: ', tags[:20], "\n")  # Prints first 20 tuples of (lemma, POS tag)

    nouns = [word for (word, tag) in tags if tag[:2] == 'NN']  # Include word if the tag starts win 'NN' (noun)

    print('Number of tokens (step a): ', len(reduced))  # Print number of tokens included in the reduced token list
    print('Number of nouns: ', len(nouns))  # Print the number of nouns
    return reduced, nouns  # Return a tuple of (list of alphabetic and len > 5 tokens, list of nouns)


# Function to get the top 50 words in the nouns list based on frequency in the tokens list
def get_top_words(tokens, nouns):
    count_dict = collections.defaultdict(list)  # Create a default dict that defaults to a list.
    top_words = []  # List of top_words
    # For every noun, count the number of times it appears in tokens and then append the noun
    # to the list of nouns corresponding to the number of occurrences. This makes it easier to
    # sort the resultant dictionary based on frequency
    for noun in nouns:
        count_dict[tokens.count(noun)].append(noun)
    sort_count = sorted(list(count_dict.keys()), reverse=True)  # Sort the keys in descending order based on value
    i = 1  # Counter to make sure exactly 50 nouns are added
    # For every noun frequency, iterate through the list of nouns.
    for count in sort_count:
        for word in count_dict[count]:
            if i > 50:  # If more than 50 words, stop.
                break
            top_words.append(word)  # Append the word to the list of top 50 words
            print(i, ': ', word, count)  # Print out the 50 most common words and the respective count
            i += 1  # Increment word counter
    return top_words    # Return the list of top 50 words


# Overhead for the guessing game to function
# top_words: Is the top 50 words passed into the function
def guessing_game(top_words):
    points = 5  # Start with 5 points
    loop = True     # Set the loop condition as True
    while loop:     # While we want to keep playing games:
        rand_word = top_words[randint(0, len(top_words) - 1)]   # Get the random word
        char_idx = {}   # Create a dictionary to keep track of each letter and which indices the letter fills
        # The below loop essentially just uses the letter as a key and matches the corresponding indices as values.
        for i in range(len(rand_word)):
            if rand_word[i] not in char_idx:
                char_idx[rand_word[i]] = []
            char_idx[rand_word[i]].append(i)
        hidden = ['-'] * len(rand_word)     # The hidden string is converted to a list because strings are immutable
        print('\nLet\'s play a word guessing game!\n')  # Let user know guessing game has begun
        # game_loop has actual game functionality. Returns False if exclamation mark is encountered.
        cont = game_loop(points, hidden, char_idx, rand_word)
        if not cont:
            break
        loop = play_again()     # Check if we want to play again or not
    print('\nGoodbye cruel world!\n')   # Program dies :(


# Checks to see if player wants to play again
def play_again():
    valid = False   # Set to false
    while not valid:
        inp = input('\nPlay again? (Y/N): ')    # Ask the user to continue
        valid = True    # Assume we want to continue to avoid further checks
        if inp.lower() == 'n':  # If we don't want to continue
            valid = False   # Set valid to False and break out of the loop to return that we don't want to continue
            break
        elif inp.lower() != 'y':    # If the input doesn't match the format, ask again
            print('Please enter Y/N')
            valid = False   # Set valid to False again to ensure the loop continues
    return valid    # Return whether or not we want to continue


# The inner functionality of the game
# - points: Number of points we start with
# - hidden: The list containing the word masked with '-' characters. To be filled in by player.
# - char_idx: The dictionary containing the character and indices the characters fill
# - word: The actual word. Used to tell the user what the word was if they lost the game.
def game_loop(points, hidden, char_idx, word):
    inc = 0     # Keeps track of how many letters have been filled in
    used = {}   # Keeps track of letter already guessed
    # While we still have 0 or more points and we haven't completely guessed the word:
    while points > -1 and inc < len(hidden):
        print(''.join(hidden))  # Print out the current state of the guessed word
        print('Current Score: ', points)    # Print out the current score
        inp = input('Guess a letter: ')     # Asks player to guess a letter
        # If the letter has already been guessed, ask them to guess a different letter WITHOUT subtracting score
        if inp in used:
            print('Letter already guessed. Please guess a different letter.')
            continue
        if inp == '!':  # If the player enters '!', return False to indicate we want to stop playing
            return False
        used[inp] = True    # We have officially used the letter; add it to used{}
        if not inp.isalpha() or not len(inp) == 1:  # Ensures only a character is used as input
            print('Input can only be a character!')
            continue
        if inp in char_idx:     # If input is in the char_idx
            print('Right! Score increased by 1')    # Tell the user they got it right
            for idx in char_idx[inp]:   # Fill the indices with the guessed character
                hidden[idx] = inp
            points += 1     # Increase the points by 1
            inc += len(char_idx[inp])   # Increase the number of characters guessed by number of indices
        else:   # Otherwise, tell user they guessed wrong and decrease score by 1
            print('Incorrect. Score decreased by 1')
            points -= 1
    if inc == len(hidden):  # If the number of correctly guessed characters equals the len of word, win the game
        print('\nCongratulations! You won!')
    else:   # Otherwise, you lost :(
        print('\nYou lost. The word was \'' + word + '\'.\n')
    return True     # Return True to indicate the user didn't input '!'


# Main function to enclose variables and to handle printing
def main():
    raw_text = open_file()  # Open file
    diverse_score = lexical_diversity(raw_text)     # Calculate lexical diversity
    print('\nLexical diversity is: %.2f\n' % diverse_score)     # Print lexical diversity

    tokens, nouns = preprocess(raw_text)    # Preprocess the text
    top_words = get_top_words(tokens, nouns)    # Get the top 50 words

    guessing_game(top_words)    # Start the guessing games with the top 50 words


# Makes sure only one argument for file path is given by player. Also allows program to be run as main.
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Give exactly ONE argument as path name!')
        quit()
    main()  # If valid, pass to main()
