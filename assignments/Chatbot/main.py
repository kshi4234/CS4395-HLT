import collections
import math
import operator
from bs4 import BeautifulSoup
import requests
import os
from nltk import sent_tokenize, word_tokenize
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from nltk.corpus import stopwords
import csv
from gensim import models, corpora
from gensim.models.coherencemodel import CoherenceModel


stopwords = stopwords.words('english')

directory_raw = 'raw'
directory_sent = 'sent'
NUM_TOPICS = 10


def crawl(start_url):
    r = requests.get(start_url)
    data = r.text
    soup = BeautifulSoup(data, features='html.parser')
    links = [start_url]
    counter = 1
    for link in soup.find_all('a'):
        link_str = str(link.get('href'))
        if link_str.startswith('/wiki') and 'google' not in link_str and 'archive' not in link_str and '/Special' not in link_str and '/ISBN' not in link_str:
            print(link_str)
            links.append('https://en.wikipedia.org' + link_str)
            counter += 1
        if counter > 150:
            break
    return links


def scrape(links):
    if not os.path.exists(directory_raw):
        os.makedirs(directory_raw)
    for i, link in enumerate(links):
        file = str(i) + '.txt'
        path = os.path.join(directory_raw, file)
        if os.path.exists(path):
            continue
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        session.mount('https://', adapter)
        try:
            r = session.get(link)
            r.raw.chunked = True
            r.encoding = 'utf-8'
        except requests.exceptions.ConnectionError:
            continue

        data = r.text
        soup = BeautifulSoup(data, features='html.parser')
        soup.prettify('UTF-8')
        with open(path, 'w', encoding='UTF-8') as f:
            # f.write(str(soup))
            for p in soup.find_all('p'):
                # f.write(str(p))
                text = p.text
                # print(p)
                # print('trying!')
                # print(p.text)
                if text:
                    f.write(text + '\n')


def process():
    if not os.path.exists(directory_sent):
        os.makedirs(directory_sent)
    for file in os.listdir(directory_raw):
        with open(os.path.join(directory_raw, file), 'r', encoding='UTF-8') as f:
            text = f.read()
            text = ' '.join(text.split())
            if text and len(text.split()) > 80:
                tokens = sent_tokenize(text)
                with open(os.path.join(directory_sent, file), 'w', encoding='UTF-8') as g:
                    for token in tokens:
                        if token[0] == '[' and token[1].isdigit():
                            token = ' '.join(token.split()[1:])
                        g.write(token + '\n')


def calc_tf_idf():
    tf_idf = collections.defaultdict(float)
    num_docs = 0
    document_counts = collections.defaultdict(int)
    all_raw = ''
    all_text = []
    split_text = []

    # Some preprocessing to collect all data so we don't have to keep opening files
    for file in os.listdir(directory_sent):
        with open(os.path.join(directory_sent, file), 'r', encoding='UTF-8') as f:
            raw = f.read()
            all_raw += raw
            raw = raw.lower()
            all_text += [w for w in word_tokenize(raw) if w.isalpha() and w not in stopwords]
            split_text.append([w for w in word_tokenize(raw) if w.isalpha() and w not in stopwords])
            num_docs += 1

    # Get number of occurrences across documents
    set_text = set(all_text)
    for word in set_text:
        for raw_text in split_text:
            if word in set(raw_text):
                document_counts[word] += 1

    # Calculate tf for each document and then calculate tf-idf
    for raw_text in split_text:
        counts = collections.Counter(raw_text)
        for word in counts.keys():
            tf = counts[word] / len(raw_text)
            # print(word, counts[word])
            idf = math.log(num_docs / (1 + document_counts[word]))
            tf_idf[word] = max(tf * idf, tf_idf[word])
    print('Done3')
    return tf_idf, all_raw


def get_topics():
    all_text = []
    global NUM_TOPICS
    # Some preprocessing to collect all data so we don't have to keep opening files
    for file in os.listdir(directory_sent):
        with open(os.path.join(directory_sent, file), 'r', encoding='UTF-8') as f:
            raw = f.read()
            raw = raw.lower()
            sentences = sent_tokenize(raw)
            for sentence in sentences:
                all_text.append([w for w in word_tokenize(sentence) if w.isalpha() and w not in stopwords])
    # print(all_text[:50])
    dictionary = corpora.Dictionary(all_text)
    corpus = [dictionary.doc2bow(tokens) for tokens in all_text]
    lda_model = models.LdaModel(corpus=corpus, num_topics=NUM_TOPICS, id2word=dictionary)

    print("LDA Model 1 Perplexity:", lda_model.log_perplexity(corpus))

    coherence1 = CoherenceModel(model=lda_model,
                                texts=all_text, dictionary=dictionary, coherence='u_mass')
    print('Coherence score:', coherence1.get_coherence())
    return lda_model, dictionary


def main():
    start_url = 'https://en.wikipedia.org/wiki/Basketball'   # Start URL
    links = crawl(start_url)    # Crawl and return links

    # Print collected links
    for i, link in enumerate(links):
        print(i, link)

    # scrape(links)   # Scrape contents of webpages from links
    # process()   # Process the data and move to sentence tokenized files
    lda_model, dictionary = get_topics()
    print("LDA Model Results")
    for i in range(NUM_TOPICS):
        print("\nTopic #%s:" % i, lda_model.print_topic(i, 20))
    tf_idf_dict, all_raw = calc_tf_idf()    # Calculate tf-idf scores and then
    tf_idf_dict = sorted(tf_idf_dict.items(), key=lambda item: item[1], reverse=True)

    top = []
    for i in range(200):
        print(tf_idf_dict[i][0])
        top.append(tf_idf_dict[i][0])

    # Create knowledge base as dictionary
    kb = collections.defaultdict(list)
    sentences = set(sent_tokenize(all_raw))
    for word in top:
        for sentence in sentences:
            if word in sentence.lower().split():
                kb[word].append(sentence)

    # Put dictionary knowledge base into a csv format for easier visual access
    with open('my_kb.csv', 'w', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['word', 'related fact'])
        for word, sentences in kb.items():
            for sent in sentences:
                w.writerow([word, sent])

    # DEBUG code for printing out knowledge base and is not really necessary.
    # Disable if unneeded.
    # for word in kb:
    #     for sent in kb[word]:
    #         print(word, sent)


if __name__ == '__main__':
    main()
