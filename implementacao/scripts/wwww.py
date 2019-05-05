from pymongo import MongoClient

client = MongoClient('localhost', 27017)

news_2018 = client['news_2018']
news = client['news']

for article in news['folha'].find(no_cursor_timeout=True):
    if float(datetime.datetime.fromtimestamp(int(article['date'])).strftime('%Y')) == 2018:
        # compute title size
        title_size = len(str(article['title']).split())

        # compute text size
        text_size = len(str(article['text']).split())

        # compute number of comments
        number_comments = news['folhaComments'].count_documents({'id_article' : article['id_article']})

        # comments
        for comment in news['folhaComments'].find({"id_article" : article['id_article']}, no_cursor_timeout=True):
                # insert comments in news_2018
                news_2018['folhaComments'].insert_one(comment)

        # insert article
        news_2018['folha'].insert_one(article)

        # insert metadata
        news_2018['MetaData'].insert_one({
                'article_url' : article['url'],
                'text_size' : text_size,
                'number_comments' : number_comments
        })
