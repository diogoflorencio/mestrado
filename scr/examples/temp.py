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

from readcalc import readcalc
from pymongo import MongoClient
import nltk
nltk.download('punkt')
client = MongoClient('localhost', 27017)
db = client['mestrado']
collections = ['oantagonistaComments', 'ogloboComments', 'vejaComments']

for collection in collections:
   
    for comment in db[collection].find(no_cursor_timeout=True).batch_size(5):
        text_readability = readcalc.ReadCalc(text=lexical_normalization(comment['text']), language="pt_BR")
        
        db[collection].update_one({'_id' : comment['_id']}, 
                         {'$set' : {'words':len(text_readability.get_words()),
                                    'unique_words':text_readability.get_internal_metrics()[2],
                                    'chars':text_readability.get_internal_metrics()[0],
                                    'sentences':len(text_readability.get_sentences()),
                                    'syllables':text_readability.get_internal_metrics()[4],
                                    '3_syllables_or_more':text_readability.get_internal_metrics()[5],                                    
                                    'flesch_reading_ease': text_readability.get_flesch_reading_ease(),
                                    'flesch_kincaid_grade_level': text_readability.get_flesch_kincaid_grade_level(),
                                    'coleman_liau_index': text_readability.get_coleman_liau_index(),
                                    'gunning_fog_index': text_readability.get_gunning_fog_index(),
                                    'smog_index':text_readability.get_smog_index(),
                                    'ari_index':text_readability.get_ari_index(),
                                    'lix_index':text_readability.get_lix_index(),
                                    'dale_chall_score':text_readability.get_dale_chall_score(),
                                    'dale_chall_known_fraction':text_readability.get_dale_chall_known_fraction()
                                   }
                         })        
