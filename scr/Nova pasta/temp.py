import nltk
import re
from gensim.models import KeyedVectors
from pymongo import MongoClient
from nltk.corpus import stopwords
nltk.download('stopwords')

PUNCTUATION = u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ%]' # define news punctuation 
SENTENCE_SIZE_THRESHOLD = 2 # Minimum length of a text
HOST_IP = 'localhost' # define host's ip

# loading abbreviation dic
with open('../dics/AB_dict') as f:
    abbreviation = f.readlines()
# process dic    
abbreviation = [x.split() for x in abbreviation]
abbreviation = {line[0]: line[1] for line in abbreviation}

# loading internet_slang dic
with open('../dics/IN_dict') as f:
    internet_slang = f.readlines()
# process dic    
internet_slang = [x.split() for x in internet_slang]
internet_slang = {line[0]: ' '.join(line[1:]) for line in internet_slang}

# loading foreign_word dic
with open('../dics/ES_dict') as f:
    foreign_word = f.readlines()
# process dic    
foreign_word = [x.split() for x in foreign_word]
foreign_word = [line for line in foreign_word if len(line) > 1] # selecting valid lines
foreign_word = {line[0]: ' '.join(line[1:]) for line in foreign_word}

# Lexical normalization
def lexical_normalization(text):
    for k, v in abbreviation.items():
        text = str(text).replace(k,v)        
    for k, v in internet_slang.items():
        text = str(text).replace(k,v)        
    for k, v in foreign_word.items():
        text = str(text).replace(k,v)
    return text

# function for processing text
def process_sentences(text):
    stop_words = stopwords.words('portuguese') # load stop words
    text = text.split() # split sentences by words
    text = [word for word in text if word not in stop_words] # Remove stopwords
    return " ".join(text)

w2v =  KeyedVectors.load_word2vec_format('../embeddings/news_vectors.bin', binary=False)

# init client mongo
client = MongoClient(HOST_IP, 27017)
# select db
db = client['news_2018']
# define colelctions
collections = ["oantagonista", "oglobo", "veja"]

for collection in collections:
    len_collection = db[collection].count_documents({})
    index = 0
    for article in db[collection].find({}, no_cursor_timeout=True).batch_size(5):
        # Processing text
        article_text = process_sentences(article["text"]) 
        for comment in db[collection + "Comments"].find({'id_article': article["url"]}, no_cursor_timeout=True).batch_size(5):
            # Processing comment text
            comment_text = lexical_normalization(comment["text"])
            comment_text = process_sentences(comment["text"])
            # Insert wmd in database
            db["alignmentNewsComments"].insert_one({
                                                        'article': article['url'],
                                                        'comment': comment['_id'],
                                                        'wmd': w2v.wmdistance(article_text, comment_text)
                                                   })
        # print status
        index += 1
        print('Portal: {0} - Progress: {1:.4f} %'.format(collection, index / len_collection * 100), end='\r')  