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


stopwords = stopwords.words('english')

directory_raw = 'raw'
directory_sent = 'sent'


def crawl(start_url):
    r = requests.get(start_url)
    data = r.text
    soup = BeautifulSoup(data, features='html.parser')
    links = []
    counter = 1
    for link in soup.find_all('a'):
        link_str = str(link.get('href'))
        if link_str.startswith('http') and 'google' not in link_str and 'archive' not in link_str and '.com' in link_str:
            links.append(link_str)
            counter += 1
        if counter > 30:
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
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        try:
            r = session.get(link)
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
            if text:
                tokens = sent_tokenize(text)
                with open(os.path.join(directory_sent, file), 'w', encoding='UTF-8') as g:
                    for token in tokens:
                        g.write(token + '\n')


def calc_tf_idf():
    tf_idf = {}
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
            tf_idf[word] = tf * idf
    print('Done3')
    return tf_idf, all_raw


def main():
    start_url = 'https://en.wikipedia.org/wiki/Space_exploration'   # Start URL
    links = crawl(start_url)    # Crawl and return links

    # Print collected links
    for i, link in enumerate(links):
        print(i, link)

    scrape(links)   # Scrape contents of webpages from links
    process()   # Process the data and move to sentence tokenized files
    tf_idf_dict, all_raw = calc_tf_idf()    # Calculate tf-idf scores and then
    tf_idf_dict = sorted(tf_idf_dict.items(), key=lambda item: item[1], reverse=True)
    for i in range(25):
        print(tf_idf_dict[i][0])

    # Manually determined top-10 words
    top_ten = ['tsiolkovsky', 'hawking', 'starshot', 'station', 'mangalyaan', 'planets', 'stars', 'redshift', 'breakthrough', 'kilometres']

    # Create knowledge base as dictionary
    kb = collections.defaultdict(list)
    sentences = sent_tokenize(all_raw)
    for word in top_ten:
        for sentence in sentences:
            if word in sentence.lower():
                kb[word].append(sentence)

    # Put dictionary knowledge base into a csv format for easier visual access
    with open('my_kb.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(['word', 'related fact'])
        for word, sentences in kb.items():
            for sent in sentences:
                w.writerow([word, sent])

    # DEBUG code for printing out knowledge base and is not really necessary.
    # Disable if unneeded.
    for word in kb:
        for sent in kb[word]:
            print(word, sent)


if __name__ == '__main__':
    main()
