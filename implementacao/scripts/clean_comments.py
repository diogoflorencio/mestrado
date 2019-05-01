from pymongo import MongoClient
import datetime

client = MongoClient('localhost', 27017)
db = client.news
collections = ['oantagonista', 'oglobo', 'veja']

for collection in collections:
    print('\n' + collection + '\n')

    for comment in db[collection + 'Comments'].find():
        try:
            #process Comment
            if float(datetime.datetime.fromtimestamp(int(comment['date'])).strftime('%Y')) < 2010:
                print('delete comment' + str(datetime.datetime.fromtimestamp(int(comment['date']))))
                db[collection  + 'Comments'].delete_one({'_id':comment['_id']})

            elif float(datetime.datetime.fromtimestamp(int(comment['date'])).strftime('%Y')) > 2018:
                print('delete comment' + str(datetime.datetime.fromtimestamp(int(comment['date']))))
                db[collection  + 'Comments'].delete_one({'_id':comment['_id']})
        except:
            print('delete comment except')
            db[collection + 'Comments'].delete_one({'_id':comment['_id']})
