import re
import nltk
import pickle
import string
import pandas as pd
import numpy as np

tokenizer = nltk.tokenize.ToktokTokenizer()
stemmer = nltk.stem.snowball.SnowballStemmer('english')
lemmatizer = nltk.stem.WordNetLemmatizer()
punctuations = string.punctuation + string.digits
stop_words = set(nltk.corpus.stopwords.words('english'))
alphabet_string = string.ascii_lowercase
alphabet_list = list(alphabet_string) + ['+', '#']
for alpha in ['r', 'c', 'm', 'e', 'q', 'n', 'j', 'd']:
    alphabet_list.remove(alpha)

def strip_list_noempty(lst):
    new_list = (item.strip() if hasattr(item, 'strip') else item for item in lst)
    return [item for item in new_list if item != '']

def clean_punctuation(text): 
    tokens = tokenizer.tokenize(text)
    punctuation_filtered = []
    regex = re.compile('[%s]' % re.escape(punctuations))

    # load used_tag_filter.pkl 
    with open('vectorizers/used_tag_filter.pkl', 'rb') as f:
        used_tag_filter = pickle.load(f)

    for token in tokens:
        if token in set(used_tag_filter):
            punctuation_filtered.append(token)
        else:
            punctuation_filtered.append(regex.sub('', token))
  
    filtered_list = strip_list_noempty(punctuation_filtered)
        
    return ' '.join(map(str, filtered_list))

def clean_text(text):
    text = text.lower()
    text = re.sub(re.compile('[\n\r\t]'), ' ', text)
    # remove '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' except some appearing as a tag
    text = clean_punctuation(text)
    # replace any sequence of 2 or more spaces with a single space
    text = re.sub(re.compile('\s{2,}'), ' ', text)
    # remove stop words and remove single character, except for 'c' and 'r' 
    text = ' '.join([token for token in tokenizer.tokenize(text) if token not in stop_words and token not in alphabet_list])
    return text

def tokenize(text):
    # tokenize
    words = tokenizer.tokenize(text)
    
    # stem first then lemmatize word list
    lem_words = [lemmatizer.lemmatize(word) for word in words]
    stem_words = [stemmer.stem(word) for word in lem_words]
    final_tokens = ' '.join(stem_words).strip()
    return final_tokens

def vectorize(text, model_choice):
    if model_choice == 'bow':
        with open('vectorizers/bow_vectorizer.pkl', 'rb') as f:
            bow_vectorizer = pickle.load(f)
        x_text = bow_vectorizer.transform(text)
        x_text_df = pd.DataFrame(x_text.toarray(), columns=bow_vectorizer.get_feature_names())
    elif model_choice == 'ngram':
        with open('vectorizers/ngram_vectorizer.pkl', 'rb') as f:
            ngram_vectorizer = pickle.load(f)
        x_text = ngram_vectorizer.transform(text)
        x_text_df = pd.DataFrame(x_text.toarray(), columns=ngram_vectorizer.get_feature_names())
    else:
        with open('vectorizers/tfidf_vectorizer.pkl', 'rb') as f:
            tfidf_vectorizer = pickle.load(f)
        x_text = tfidf_vectorizer.transform(text)
        x_text_df = pd.DataFrame(x_text.toarray(), columns=tfidf_vectorizer.get_feature_names())
    return x_text_df