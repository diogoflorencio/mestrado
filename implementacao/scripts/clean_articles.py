from pymongo import MongoClient
import datetime

client = MongoClient('localhost', 27017)
db = client.news
collections = ['carta_capital', 'estadao', 'folha', 'g1', 'oantagonista', 'oglobo', 'veja']

for collection in collections:
    print('\n' + collection + '\n')

    for article in db[collection].find():
        try:
            #process Article
            if float(datetime.datetime.fromtimestamp(int(article['date'])).strftime('%Y')) < 2010:
                print('delete article' + str(datetime.datetime.fromtimestamp(int(article['date']))))
                db[collection].delete_one({'_id':article['_id']})

            elif float(datetime.datetime.fromtimestamp(int(article['date'])).strftime('%Y')) > 2018:
                print('delete article' + str(datetime.datetime.fromtimestamp(int(article['date']))))
                db[collection].delete_one({'_id':article['_id']})
        except:
            print('delete article except')
            db[collection].delete_one({'_id':article['_id']})
