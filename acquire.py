import unicodedata
import re
import json
import os
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import requests
import nltk


# This function will create a dictionary of the wanted data.
def parse_person(person):
    name = person.h2.text
    quote = person.p.text.strip()
    email = person.select('.email')[0].text
    phone = person.select('.phone')[0].text
    address = [l.strip() for l in person.select('p')[-1].text.split('\n')[1:3]]

  
    return {
        'name': name, 'quote': quote, 'email': email,
        'phone': phone,
        'address': address
    }


# This function takes in a url as an argument and parse the contents.
def parse_blog(url):
    url = url.get('href')
    response = get(url, headers={'user-agent': 'Codeup DS Hopper'})
    blog = BeautifulSoup(response.text)
    title = blog.h1.text
    date_source = blog.p.text
    content = blog.find_all('div',class_ = 'entry-content')[0].text
      
    return {
        'title': title, 'date & source': date_source, 'content': content
    }

# This function will loop through a list of urls and return a dataframe.
def get_codeup_blogs(cached=False):
    if cached == True:
        df = pd.read_json('codeup_blogs.json')
        return df
    else:
        # Fetch data
        response = get('https://codeup.com/blog/', headers={'user-agent':'Codeup DS Hopper'})
        soup = BeautifulSoup(response.text)
        urls = soup.find_all('a',class_ = 'more-link')
        
        blog_df = pd.DataFrame([parse_blog(url) for url in urls])
        # save the dataframe as json:
        blog_df.to_json('codeup_blogs.json')
    
        return blog_df

# This function will return the text from an online article.
def get_article_text():
    # Read data locally if it exists.
    if os.path.exists('article.txt'):
        with open('article.txt') as f:
            return f.read()
    # Fetch data
    url = 'https://codeup.com/data-science/math-in-data-science/'
    headers = {'User-Agent': 'Codeup Data Science'}
    response = get(url, headers=headers)
    soup = BeautifulSoup(response.text)
    article = soup.find('div', id='main-content')
    
    # Save it for when needed
    with open('article.txt', 'w') as f:
        f.write(article.text)
    
    return article.text



def get_inshorts():
    urls = ['https://inshorts.com/en/read/science', 'https://inshorts.com/en/read/business','https://inshorts.com/en/read/sports','https://inshorts.com/en/read/technology','https://inshorts.com/en/read/entertainment']
    # Create an empty list, articles, to hold the dictionaries for each article.
    articles = []
    for url in urls:
        # Make request to 'https://inshorts.com/en/read/science'
        response = requests.get(url)
        # Use BeautifulSoup to store response content.
        soup = BeautifulSoup(response.text)
        cards = soup.find_all('div', class_='news-card')
        # Loop through each news card on the page and get what we want
        for card in cards:
            title = card.find('span', itemprop='headline' ).text
            author = card.find('span', class_='author').text
            content = card.find('div', itemprop='articleBody').text
            category = url[29:]
            
            # Create a dictionary, article, for each news card
            article = {'title': title, 'category': category, 'author': author, 'content': content}
            
            # Add the dictionary, article, to our list of dictionaries, articles.
            articles.append(article)
    return pd.DataFrame(articles)


'''========================================================================'''
def basic_clean(string):
    # Lowercase everything in the text.
    lower = string.lower()
    lower = unicodedata.normalize('NFKD', lower)\
    .encode('ascii', 'ignore')\
    .decode('utf-8', 'ignore')
    # Remove anything that isn't a-z, a number, single quote, or whitespace.
    cleaned = re.sub(r"[^a-z0-9'\s]", '', lower)
    return cleaned

def tokenize(string):
    tokenizer = nltk.tokenize.ToktokTokenizer()
    return tokenizer.tokenize(string, return_str=True)

def stem(string):
    # Create the nltk stemmer object, then use it
    ps = nltk.porter.PorterStemmer()
    stems = [ps.stem(word) for word in string.split()]
    article_stemmed = ' '.join(stems)
    return article_stemmed

def lemmatize(string):
    wnl = nltk.stem.WordNetLemmatizer()
    lemmas = [wnl.lemmatize(word) for word in string.split()]
    article_lemmatized = ' '.join(lemmas)
    return article_lemmatized

def remove_stopwords(string):
    stopword_list = stopwords.words('english')
    words = string.split()
    filtered_words = [w for w in words if w not in stopword_list]
    print('Removed {} stopwords'.format(len(words) - len(filtered_words)))
    print('---')
    string_without_stopwords = ' '.join(filtered_words)
    return string_without_stopwords

# This function will take in a dataframe of news/blog articles and if a column called 'content' exists, it will prepare the text in three different ways.
def prep_text(df):
    if 'content' in df.columns:
        df.content = df.content.str.replace('\n',' ')
        df.content = df.content.str.strip()
        df['clean'] = df.content.apply(basic_clean)
        df['stemmed'] = df.content.apply(stem)
        df['lemmatized'] = df.content.apply(lemmatize)
        return df
    else:
        print("Dataframe does not have required column 'content'.")
        
'''========================================================================'''