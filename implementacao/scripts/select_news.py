from pymongo import MongoClient
import datetime
import time
import re

client = MongoClient('localhost', 27017)

news = client.news
news_2018 = client.news_2018
collections = ['carta_capital', 'estadao', 'folha', 'g1', 'oantagonista', 'oglobo', 'veja']
PONTUACAO = u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ%.]'

for collection in collections:

	print('\n' + collection + '\n')

	for article in news[collection].find():
		if float(datetime.datetime.fromtimestamp(int(article['date'])).strftime('%Y')) == 2018:
			try:
				article['section'] = re.sub(PONTUACAO, ' ', str(article['section'])).lower()
				article['text'] = re.sub(PONTUACAO, ' ', str(article['text'])).lower()
		
				news_2018[collection].insert_one(article)
			except:
				print("Error")
