from pymongo import MongoClient

client = MongoClient('localhost', 27017)

news = client.news
veja = client.news_veja
collections = ['veja']

for collection in collections:

	print('\n' + collection + '\n')

	for article in veja[collection].find():
		try:
			news[collection].insert_one(article)
		except:
			print("Article duplicate")