from pymongo import MongoClient
import datetime
import time

client = MongoClient('localhost', 27017)
db = client.news

collections = ['carta_capital', 'estadao', 'folha', 'g1', 'oantagonista', 'oglobo', 'veja']

date_init  = float(time.mktime(datetime.datetime.strptime("01/01/2010", "%d/%m/%Y").timetuple()))
date_end  = float(time.mktime(datetime.datetime.strptime("31/12/2018", "%d/%m/%Y").timetuple()))

for collection in collections:
    print("\n{0} clean articles\n".format(collection))
    db[collection].delete_many({"$or":[{"date":{"$lt": date_init}}, {"date":{"$gt": date_end}}, {"date": {"$eq": float("NaN")}}]})

# for collection in collections[4:]:
#     print("\n{0} clean comments\n".format(collection))
#     db[collection + 'Comments'].delete_many({"$or":[{"date":{"$lt": date_init}}, {"date":{"$gt": date_end}}, {"date": {"$eq": float("NaN")}}]})
 