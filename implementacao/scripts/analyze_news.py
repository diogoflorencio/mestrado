# script to analyze the databasea
from pymongo import MongoClient
import datetime

client = MongoClient('localhost', 27017)
db = client.tmp
collection = "veja"

def init_dict():
    dictionary = {
        "2010":0,
        "2011":0,
        "2012":0,
        "2013":0,
        "2014":0,
        "2015":0,
        "2016":0,
        "2017":0,
        "2018":0,
        "2019":0
    }
    return dictionary

dist_article_year = init_dict()
for article in db[collection].find():
    dist_article_year[datetime.datetime.fromtimestamp(int(article['date'])).strftime('%Y')] +=1
print(dist_article_year)

# dist_commments_year = init_dict()
# for comment in db[collection + 'Comments'].find():
#     dist_commments_year[datetime.datetime.fromtimestamp(int(comment['date'])).strftime('%Y')] +=1
# print(dist_commments_year)

# for comment in db[collection + 'Comments'].find():
#     if db[collection].find({'id_article':comment['id_article']}).count() == 0:
#         print('delete comment: {0} without article'.format(comment['_id']))
#         db[collection + 'Comments'].delete_one({'_id':comment['_id']})
#
#     if db[collection + 'Comments'].find({
#         'author':comment['author'],
#         'text':comment['text'],
#         'id_article':comment['id_article']}).count() > 1:
#      db[collection + 'Comments'].delete_one({'_id':comment['_id']})
#      print('delete comment duplicate')
