# -*- coding: utf-8 -*-
from __future__ import print_function
import pandas as pd
import numpy as np
import nltk
import re
from nltk.corpus import stopwords
nltk.download('stopwords')
from gensim.models import KeyedVectors
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import euclidean_distances
from pyemd import emd
PUNCTUATION = u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ%]' # define news punctuation 

# VARS

#  Lexicons definition
argumentacao = "a_ponto ao_menos apenas ate ate_mesmo incluindo inclusive mesmo nao_mais_que nem_mesmo no_minimo o_unico a_unica pelo_menos quando_menos quando_muito sequer so somente a_par_disso ademais afinal ainda alem alias como e e_nao em_suma enfim mas_tambem muito_menos nao_so nem ou_mesmo por_sinal tambem tampouco assim com_isso como_consequencia consequentemente de_modo_que deste_modo em_decorrencia entao logicamente logo nesse_sentido pois por_causa por_conseguinte por_essa_razao por_isso portanto sendo_assim ou ou_entao ou_mesmo nem como_se de_um_lado por_outro_lado mais_que menos_que tanto quanto tao como desde_que do_contrario em_lugar em_vez enquanto no_caso quando se se_acaso senao de_certa_forma desse_modo em_funcao enquanto isso_e ja_que na_medida_que nessa_direcao no_intuito no_mesmo_sentido ou_seja pois porque que uma_vez_que tanto_que visto_que ainda_que ao_contrario apesar_de contrariamente contudo embora entretanto fora_isso mas mesmo_que nao_obstante nao_fosse_isso no_entanto para_tanto pelo_contrario por_sua_vez porem posto_que todavia"
modalizacao = "achar aconselhar acreditar aparente basico bastar certo claro conveniente crer dever dificil duvida efetivo esperar evidente exato facultativo falar fato fundamental imaginar importante indubitavel inegavel justo limitar logico natural necessario negar obrigatorio obvio parecer pensar poder possivel precisar predominar presumir procurar provavel puder real recomendar seguro supor talvez tem tendo ter tinha tive verdade decidir"
valoracao = "absoluto algum alto amplo aproximado bastante bem bom categorico cerca completo comum consideravel constante definitivo demais elevado enorme escasso especial estrito eventual exagero excelente excessivo exclusivo expresso extremo feliz franco franqueza frequente generalizado geral grande imenso incrivel lamentavel leve maioria mais mal melhor menos mero minimo minoria muito normal ocasional otimo particular pena pequeno pesar pior pleno pobre pouco pouquissimo praticamente prazer preciso preferir principal quase raro razoavel relativo rico rigor sempre significativo simples tanto tao tipico total tremenda usual valer"
sentimento = "abalar abater abominar aborrecer acalmar acovardar admirar adorar afligir agitar alarmar alegrar alucinar amar ambicionar amedrontar amolar animar apavorar apaziguar apoquentar aporrinhar apreciar aquietar arrepender assombrar assustar atazanar atemorizar aterrorizar aticar atordoar atormentar aturdir azucrinar chatear chocar cobicar comover confortar confundir consolar constranger contemplar contentar contrariar conturbar curtir debilitar decepcionar depreciar deprimir desapontar descontentar descontrolar desejar desencantar desencorajar desesperar desestimular desfrutar desgostar desiludir desinteressar deslumbrar desorientar desprezar detestar distrair emocionar empolgar enamorar encantar encorajar endividar enervar enfeiticar enfurecer enganar enraivecer entediar entreter entristecer entusiasmar envergonhar escandalizar espantar estimar estimular estranhar exaltar exasperar excitar execrar fascinar frustar gostar gozar grilar hostilizar idolatrar iludir importunar impressionar incomodar indignar inibir inquietar intimidar intrigar irar irritar lamentar lastimar louvar magoar maravilhar melindrar menosprezar odiar ofender pasmar perdoar preocupar prezar querer recalcar recear reconfortar rejeitar repelir reprimir repudiar respeitar reverenciar revoltar seduzir sensibilizar serenar simpatizar sossegar subestimar sublimar superestimar surpreender temer tolerar tranquilizar transtornar traumatizar venerar" #malquerer obcecar
pressuposicao = "adivinhar admitir agora aguentar ainda antes atentar atual aturar comecar compreender conseguir constatar continuar corrigir deixar demonstrar descobrir desculpar desde desvendar detectar entender enxergar esclarecer escutar esquecer gabar ignorar iniciar interromper ja lembrar momento notar observar olhar ouvir parar perceber perder pressentir prever reconhecer recordar reparar retirar revelar saber sentir tolerar tratar ver verificar"

# Mapping words in lexicons
map_lexicons = {'a ponto':'a_ponto','ao menos ':'ao_menos ','ate mesmo ':'ate_mesmo ',
                'nao mais que ':'nao_mais_que ','nem mesmo ':'nem_mesmo ','no minimo ':'no_minimo ',
                'o unico ':'o_unico ','a unica ':'a_unica ','pelo menos ':'pelo_menos ',
                'quando menos ':'quando_menos ','quando muito ':'quando_muito ','a par disso ':'a_par_disso ',
                'e nao ':'e_nao ','em suma ':'em_suma ','mas tambem ': 'mas_tambem ','muito menos ':'muito_menos ',
                'nao so ':'nao_so ','ou mesmo ':'ou_mesmo ','por sinal ':'por_sinal ','com isso ':'com_isso ',
                'como consequencia ':'como_consequencia ','de modo que ':'de_modo_que ','deste modo ':'deste_modo ',
                'em decorrencia ':'em_decorrencia ','nesse sentido ':'nesse_sentido ','por causa ':'por_causa ',
                'por conseguinte ':'por_conseguinte ','por essa razao ':'por_essa_razao ','por isso ':'por_isso ',
                'sendo assim ':'sendo_assim ','ou entao ':'ou_entao ','ou mesmo ':'ou_mesmo ','como se ':'como_se ',
                'de um lado ':'de_um_lado ','por outro lado ':'por_outro_lado ','mais que ':'mais_que ',
                'menos que ':'menos_que ','desde que ':'desde_que ','do contrario ':'do_contrario ',
                'em lugar ':'em_lugar ','em vez ':'em_vez','no caso ':'no_caso ','se acaso ':'se_acaso ',
                'de certa forma ':'de_certa_forma ','desse modo ':'desse_modo ','em funcao ':'em_funcao ',
                'isso e ':'isso_e ','ja que ':'ja_que ','na medida que ':'na_medida_que ','nessa direcao ':'nessa_direcao ',
                'no intuito ':'no_intuito ','no mesmo sentido ':'no_mesmo_sentido ','ou seja ':'ou_seja ',
                'uma vez que ':'uma_vez_que ','tanto que ':'tanto_que ','visto que ':'visto_que ','ainda que ':'ainda_que ',
                'ao contrario ':'ao_contrario ','apesar de ':'apesar_de ','fora isso ':'fora_isso ','mesmo que ':'mesmo_que ',
                'nao obstante ':'nao_obstante ','nao fosse isso ':'nao_fosse_isso ','no entanto ':'no_entanto ',
                'para tanto ':'para_tanto ','pelo contrario ':'pelo_contrario ','por sua vez ':'por_sua_vez ','posto que ':'posto_que '
               }

# FUNCTIONS

# Minimum length of a text
SENTENCE_SIZE_THRESHOLD = 2

# Compute the validity of the text by SENTENCE_SIZE_THRESHOLD
def is_valid_text(text):    
    return (True if len(text.split()) >= SENTENCE_SIZE_THRESHOLD else False)

# Check if the word is in the vocabulary
def check_value(word):
    return (vocab_dict[word] if(word in vocab_dict) else 0)

# Compute the euclidean distances between the lexicons and the text
def lexicon_rate(lexicon, text):
    vect = CountVectorizer(token_pattern="(?u)\\b[\\w-]+\\b", strip_accents=None).fit([lexicon, text])
    v_1, v_2 = vect.transform([lexicon, text])
    v_1 = v_1.toarray().ravel()
    v_2 = v_2.toarray().ravel()
    W_ = W[[check_value(w) for w in vect.get_feature_names()]]
    D_ = euclidean_distances(W_)
    v_1 = v_1.astype(np.double)
    v_2 = v_2.astype(np.double)
    v_1 /= v_1.sum()
    v_2 /= v_2.sum()
    D_ = D_.astype(np.double)
    D_ /= D_.max()
    lex=emd(v_1, v_2, D_)
    return(lex)

# Compute bias for each lexicon dimension
def wmd_ratings(text):
    if(is_valid_text(text)):
        arg = lexicon_rate(argumentacao, text)
        mod = lexicon_rate(modalizacao, text)
        val = lexicon_rate(valoracao, text)
        sen = lexicon_rate(sentimento, text)
        pre = lexicon_rate(pressuposicao, text)
        return arg, sen, val, mod, pre
    else :
        return -1, -1, -1, -1, -1

# Convert word from text into lexicons
def word2lexicon(text):
    text = str(text) + " "
    text = re.sub(PUNCTUATION, ' ', text).lower() # remove punctuation from text
    for k, v in map_lexicons.items():
        text = text.replace(k,v)
    return text

# function for processing text
def processSentences(text):
    stop_words = stopwords.words('portuguese') # load stop words
    text = text.split() # split sentences by words
    text = [word for word in text if word not in stop_words] # Remove stopwords
    return " ".join(text)

# Load model
print('Loadding embeddings', end='\r')
wv = KeyedVectors.load_word2vec_format('embeddings/news_vectors.bin', binary=False)
wv.init_sims()
vocab_dict ={word.encode('utf-8'):vocab.index for word, vocab in wv.vocab.items()} # vocabulary
W = np.double(wv.vectors_norm) # embeddings

# load data
print('Loadding data', end='\r')
carta_capital = pd.read_csv("data/carta_capital.csv") 
estadao = pd.read_csv("data/estadao.csv")
folha = pd.read_csv("data/folha.csv") 
oantagonista = pd.read_csv("data/oantagonista.csv") 
oglobo = pd.read_csv("data/oglobo.csv") 
veja = pd.read_csv("data/veja.csv") 
# concat all news
news = pd.concat((carta_capital, folha, estadao, oantagonista, oglobo, veja), sort=False, ignore_index=True)

# Processing news
print('Processing news', end='\r')
news['text'] = news['text'].apply(word2lexicon)
news['text'] = news['text'].apply(processSentences)

# Create Columns
news['arg'] = None
news['sen'] = None
news['val'] = None
news['mod'] = None
news['pre'] = None

# Compute news bias
for index, row in news.iterrows():   
    news.loc[index,'arg'], news.loc[index,'sen'], news.loc[index,'val'], news.loc[index,'mod'], news.loc[index,'pre'] = wmd_ratings(row['text'])
    print('Index: {0} - Progress: {1:.2f} %'.format(index, (index +1) / len(news) * 100), end='\r')
  
# Write news and bias
print('Writting news', end='\r')
news.to_csv('data/que_deus_ajude.csv', encoding='utf-8')
