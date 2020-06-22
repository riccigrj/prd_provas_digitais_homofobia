import argparse
import json
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from GrabzIt import GrabzItImageOptions
from GrabzIt import GrabzItClient
import boto3
import os
import hashlib


def lambda_handler(event, contex):
    for record in event['Records']:
        doc = json.loads(record['body'])
        text = get_text(doc)
        sentiment = get_sentiment(text)
        new_doc = append_sentiment(doc, sentiment)
        if ((sentiment["score"] < -0.8)):
            screenshot = take_screenshot(doc["user"]["screen_name"], doc["id_str"])
            file_name, file_hash = save_screenshot(screenshot, doc["id_str"])
            new_doc["screenshot"] = {}
            new_doc["screenshot"]["file_path"] = file_name
            new_doc["screenshot"]["file_hash"] = file_hash
        resp = index_event(new_doc)
    return text, resp
    
def index_event(doc):
    es_data = os.environ['ES_DATA'].split(",")
    now = datetime.now()
    now_sp = now - timedelta(hours=3)
    indice = "twitter-1"+now_sp.strftime("-%Y.%m.%d")
    es = Elasticsearch(es_data)
    #resp = es.cluster.health()
    resp = es.index(index=indice, body=doc)
    return resp

def append_sentiment(doc, sentiment):
    new_doc = doc
    new_doc['sentiment'] = {}
    new_doc["sentiment"]["text"] = sentiment["text"]
    new_doc["sentiment"]["score"] = sentiment["score"]
    new_doc["sentiment"]["magnitude"] = sentiment["magnitude"]
    return new_doc
    
def get_sentiment(text):
    client = language.LanguageServiceClient()
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language= "pt-BR")
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    sentiment_doc = {}
    sentiment_doc["text"] = text
    sentiment_doc["score"] = sentiment.score
    sentiment_doc["magnitude"] = sentiment.magnitude
    return (sentiment_doc)
    
def get_text(doc):
    text= ""
    if "retweeted_status" in doc:
        if "extended_tweet" in doc["retweeted_status"]:
            if "full_text" in doc["retweeted_status"]["extended_tweet"]:
                text = doc["retweeted_status"]["extended_tweet"]["full_text"]
        elif "text" in doc["retweeted_status"]:
                text = doc["retweeted_status"]["text"]
    elif "extended_tweet" in doc:
        if "full_text" in doc["extended_tweet"]:
            text = doc["extended_tweet"]["full_text"]
    elif "text" in doc:
        text = doc["text"]
    else:
        text = None
    
    return text
def save_screenshot(screenshot, id_status):
    filepath = '/tmp/'+id_status+'.png'
    file_name = id_status+".png"
    now = datetime.now()
    now_sp = now - timedelta(hours=3)
    directory = now_sp.strftime("%Y/%m/%d/")
    s3_client = boto3.client('s3')
    with open(filepath, 'wb') as file:
        file.write(screenshot)
    hashValue = hash(filepath)
    response = s3_client.upload_file(filepath, "lgbtqia-evidencias",directory+file_name)
    os.remove(filepath)
    return file_name, hashValue
    
def hash(filepath):
    BLOCK_SIZE = 65536
    file_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)
    return (file_hash.hexdigest())

def take_screenshot(user, id_status):
    url = "https://twitter.com/"+user+"/status/"+id_status
    grabzIt = GrabzItClient.GrabzItClient("ACCESS", "SECRET")
    options = GrabzItImageOptions.GrabzItImageOptions()
    options.format = "png"
    options.delay = 3000
    grabzIt.URLToImage(url, options)
    screenshot = grabzIt.SaveTo()
    return screenshot