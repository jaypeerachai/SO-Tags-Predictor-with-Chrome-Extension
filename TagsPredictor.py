from flask import Flask, request
from flask_cors import CORS

import pickle
import json
import numpy as np
import pandas as pd

from simpletransformers.classification import (
    MultiLabelClassificationModel, MultiLabelClassificationArgs
)

from Preprocessing import clean_text, tokenize, vectorize

app = Flask(__name__)
CORS(app, support_credentials=True)

BEST_MODEL_PATH = {
    'bow': 'models/bow_logis_1.0_l1_liblinear.pkl',
    'ngram': 'models/ngram_multinomialNB_0.001.pkl',
    'tfidf': 'models/tfidf_mlp_1e-05_adaptive_False_0.0001_1000.pkl',
    'bert': 'models/distilbert'
}

@app.route('/', methods = ['POST'])
def start_flask():
    input_json = request.get_json()
    # print(input_json)
    tag_results = predict_tags(input_json)
    print(tag_results)
    return json.dumps(tag_results)

def predict_tags(input_json):
    model_choice = input_json['model']
    preprocessed_input = preprocess_input(input_json, model_choice)
    if model_choice != 'bert':
        vectorized_input = vectorize_input(preprocessed_input, model_choice)
        predicted_tags = make_prediction(
            input_json['model'],
            load_model(model_choice), 
            vectorized_input, 
            input_json['k'], 
            input_json['threshold'],
        )
    else:
        predicted_tags = make_prediction(
            input_json['model'],
            load_model(model_choice), 
            preprocessed_input, 
            input_json['k'], 
            input_json['threshold'],
        )
    return predicted_tags

def preprocess_input(input_json, model_choice):
    title = input_json['title']
    body = input_json['description']
    cleaned_title = clean_text(title)
    cleaned_body = clean_text(body)
    text = title + ' ' + title + ' ' + body

    if model_choice != 'bert':
        title_length = len(cleaned_title.split())
        body_length = len(cleaned_body.split())
        have_code = 0
        have_image = 0
        tokenized_text = tokenize(text)

        input_df = pd.DataFrame({
            'have_image': [have_image], 
            'have_code': [have_code], 
            'title_length': [title_length], 
            'body_length': [body_length], 
            'text': [tokenized_text]
        })
    else:
        input_df = text

    return input_df

def vectorize_input(input_df, model_choice):
    text_df = vectorize(input_df['text'], model_choice)
    input_df = input_df.drop(['text'], axis=1)
    input_df = pd.concat([input_df, text_df], axis=1)
    return input_df

def load_model(model_choice):
    if model_choice == 'bow':
        with open(BEST_MODEL_PATH['bow'], 'rb') as f:
            model = pickle.load(f)
    elif model_choice == 'ngram':
        with open(BEST_MODEL_PATH['ngram'], 'rb') as f:
            model = pickle.load(f)
    elif model_choice == 'tfidf':
        with open(BEST_MODEL_PATH['tfidf'], 'rb') as f:
            model = pickle.load(f)
    else:
        model = MultiLabelClassificationModel(
            "distilbert", BEST_MODEL_PATH['bert'],
            use_cuda=False,
        )
    print(model)
    return model

def make_prediction(model_choice, model, input_df, k, threshold):
    k = int(k)
    threshold = float(threshold)
    tag_dict = {}
    with open('vectorizers/y_names.pkl', 'rb') as f:
        y_names = pickle.load(f)

    if model_choice != 'bert':
        prediction = model.predict(input_df.to_numpy())
        probability = model.predict_proba(input_df.to_numpy())
    else:
        print(input_df)
        predictions, probability = model.predict(input_df)

    indexes = np.where(probability[0] >= threshold)
    predicted_tags = [y_names[index] for index in indexes[0]]
    predicted_prob = [round(probability[0][index], 4) for index in indexes[0]]
    tag_results = dict(zip(predicted_tags, predicted_prob))
    tag_results = dict(sorted(tag_results.items(), key=lambda x: x[1], reverse=True))
    if len(tag_results) > k:
        tag_results = dict(list(tag_results.items())[:k])
    tag_results = {key: "{:.2f} %".format(value*100) for key, value in tag_results.items()}

    return tag_results


if __name__ == '__main__':
    app.run()