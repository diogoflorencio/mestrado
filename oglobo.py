from pymongo import MongoClient
import datetime
import time
import re

client = MongoClient('localhost', 27017)

mestrado = client['mestrado']
news = client['news']

collections = ['oglobo']

for collection in collections:
    len_collection = mestrado[collection].count_documents({})
    index = 0
    # process collection
    for article in mestrado[collection].find(no_cursor_timeout=True).batch_size(5):
        for comment in news[collection + 'Comments'].find({'id_article': article['_id']},no_cursor_timeout=True).batch_size(5):
            try:
                comment['id_article'] = article['url']
                mestrado[collection + 'Comments'].insert_one(comment)
            except:
                pass
        index += 1
        print('Portal: {0} - Progress: {1:.4f} %'.format(collection, index / len_collection * 100), end='\r')
