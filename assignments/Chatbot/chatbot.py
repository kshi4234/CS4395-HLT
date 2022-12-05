import collections
import pandas as pd
import os
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.translate.bleu_score import SmoothingFunction
from nltk.translate.bleu_score import sentence_bleu
from sentence_transformers import SentenceTransformer, util
import pickle

model = SentenceTransformer('shafin/distilbert-similarity-b32')

smoothie = SmoothingFunction().method4
stopwords = stopwords.words('english')

question_words = ["what", "why", "when", "where", "who",
                  "name", "is", "how", "do", "does",
                  "which", "are", "could", "would",
                  "should", "has", "have", "whom", "whose", "don't, can"]


class ChatBot:
    def __init__(self):
        self.user_models = {}

    def login(self):
        name = input('>> Hi! What is your name?\nYou: ')
        print(self.user_models)
        if name in self.user_models.keys():
            print('>> Welcome back,', name + '! This is a chatbot for all things basketball related!\n')
            print('>> Type \'stop\' to quit.')
            return self.user_models[name]
        else:
            self.user_models[name] = UserModel(name)
            print(self.user_models)
            return self.user_models[name]


class UserModel:
    def __init__(self, name):
        print('>> Thanks, and welcome! This is a chatbot for all things basketball related!\n')
        print('>> Type \'stop\' to quit.')
        self.name = name
        self.tf_idf = collections.defaultdict(float)
        self.dataframe = pd.read_csv('my_kb.csv', encoding='utf-8')
        self.words = self.dataframe.word.unique()
        self.sentences = self.dataframe['related fact'].tolist()

    def take_input(self):
        user_input = input('You:')
        return user_input

    def find_similar(self, base):
        ref = model.encode(base)
        scores = []
        relevant = self.find_relevant(base)
        if not relevant:
            return None
        for sent in relevant:
            hyp = model.encode(sent)
            cos_sim = util.cos_sim(ref, hyp)
            scores.append((cos_sim.tolist()[0][0], sent))
        scores = sorted(scores, key=lambda x: x[0])
        return scores[-1]

    def find_relevant(self, base):
        relevant = []
        ref_tokens = [t.lower() for t in word_tokenize(base) if t not in stopwords and t.isalpha()]
        for sent in self.sentences:
            hyp_tokens = [t.lower() for t in word_tokenize(sent) if t not in stopwords and t.isalpha()]
            score = sentence_bleu([ref_tokens],
                                  hyp_tokens,
                                  weights=(0.5, 0.5),
                                  smoothing_function=smoothie)
            if score > 0.1:
                relevant.append(sent)
        return relevant

    def get_view(self, topic):
        return self.dataframe.loc(self.dataframe['word'] == topic)


def get_type(reference):
    tokens = word_tokenize(reference)
    if any(x in tokens[0].lower() for x in question_words) and reference[-1] == '?' or ' '.join(
            tokens[:2]).lower() == 'give me':
        return True
    else:
        return False


def main():
    if os.path.exists('chatbot.pickle'):
        with open('chatbot.pickle', 'rb') as p:
            chatbot = pickle.load(p)
    else:
        chatbot = ChatBot()

    user = chatbot.login()

    while (True):
        user_input = user.take_input()
        if user_input.lower() == 'stop':
            break
        is_question = get_type(user_input)
        output = user.find_similar(user_input)
        if not output:
            print('>> Sorry, that didn\'t really make sense to me.')
            continue
        output_token = [t.lower() for t in word_tokenize(output[1]) if t.isalpha() and t not in stopwords]
        important = [t.lower() for t in word_tokenize(user_input) if t.isalpha() and t not in stopwords]
        if is_question:
            if output[0] >= 0.05:
                print('>>', output[1])
            else:
                if any(x in important for x in output_token):
                    # print('accuracy:', output[0], 'sent:', output[1])
                    print('>>', output[1])
                else:
                    # print('accuracy:', output[0], 'sent:', output[1])
                    answer = input('>>I don\'t know, what do you think?\nYou: ')
                    print('>>Wow! Thanks for letting me know!')
                    user.sentences.append(answer)
        else:
            if output[0] >= 0.6:
                print('>>Thanks, but I already knew that. ' + output[1])
                user.sentences.append(user_input)
            else:
                # print('accuracy:', output[0], 'sent:', output[1])
                print('>>Wow! Thanks for letting me know!')
                user.sentences.append(user_input)
    with open('chatbot.pickle', 'wb') as p:
        pickle.dump(chatbot, p, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
