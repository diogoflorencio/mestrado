from pymongo import MongoClient
client = MongoClient('localhost', 27017)
tmp = client.tmp
news = client.news
collection = 'oantagonista'
for article in tmp[collection].find():
    tmp_article = {'_id':article['_id'],
    			   'title':article['title'],
           		   'section':article['section'],
           		   'date':article['date'],
                   'text':article['text'],
                   'url':article['_id']
          }
    try:
        news[collection].insert_one(tmp_article)
    except:
        print("An exception occurred")