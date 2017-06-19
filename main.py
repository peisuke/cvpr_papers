import urllib.request
import pickle
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import json

def search_paper(title):
    title_words = re.sub('[^a-zA-Z0-9]', ' ', title)
    title_words = [w for w in re.split(' +', title_words)]
    #title_words = list(filter(lambda w: len(w) == re.search(r'[a-zA-Z0-9]+', w).end(), title_words))
    title_words = ['ti:' + w for w in title_words]

    query = ''
    for i, w in enumerate(title_words):
        query += w
        query += '+AND+'
    query = query[0:-5]
    url = 'http://export.arxiv.org/api/query?search_query=' + query

    response = urllib.request.urlopen(url)
    arxiv_data = response.read()
    return arxiv_data

def get_information(arxiv_data):
    soup = BeautifulSoup(arxiv_data.decode('ascii', 'ignore'), 'lxml')
    entries = soup.findAll("html")[0].findAll('body')[0].findAll('entry')
    if len(entries) == 0:
        abstract = None
        link = None
    else:
        abstract = entries[0].findAll('summary')[0].text.strip().replace("\n", " ")
        link = entries[0].findAll('id')[0].text.strip()
    return {'link': link, 'abstract': abstract}

def main():
    print('Connecting CVPR page')
    url = 'http://cvpr2017.thecvf.com/program/main_conference'
    response = urllib.request.urlopen(url)
    html_data = response.read()
    
    print('Parsing')
    soup = BeautifulSoup(html_data.decode('ascii', 'ignore'), 'html5lib')
    
    program_table = soup.findAll("table",{"class":"table"})[3]
    tbody = program_table.findAll("tbody")[0]
    tmain = tbody.findAll("tr")
    
    info = tmain[0].findAll("th")
    
    print('Collecting')
    keys = []
    for i in info:
        keys.append(i.text.strip())
        
    data = []
    for title in tmain[1:]:
        rows = title.findAll('td')
        d = {}
        for k, v in zip(keys, rows):
            val = v.text.strip()
            if len(val) == 0:
                val = data[-1][k]
            d[k] = val
        data.append(d)
        
    for i, d in enumerate(data):
        print(i, len(data))
        title = d['Paper Title']
        print(title)
        arxiv_data = search_paper(d['Paper Title'])
        ret = get_information(arxiv_data)
        print(ret['link'])
        d['link'] = ret['link']
        d['abstract'] = ret['abstract']
        time.sleep(1)
    
    with open('cvpr.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    main()
