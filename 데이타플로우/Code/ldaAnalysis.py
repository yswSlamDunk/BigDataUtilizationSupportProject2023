import os
import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm

import gensim
from gensim import corpora

from config import *

def startLDA(ldaConfig):
    df = pd.read_excel(ldaConfig['inputPath'])
    series = df[ldaConfig['keywordColumn']]
    dictionary, corpus = makeCorpus(series)

    for numTopic in tqdm(ldaConfig['numTopics']):
        ldaModel = gensim.models.ldamodel.LdaModel(corpus, num_topics = numTopic,
                                                   id2word = dictionary, passes = 15)
        with open(ldaConfig['outputPath'] + f'topicNum_{str(numTopic)}.pickle', 'wb') as f:
            pickle.dump((ldaModel, dictionary, corpus), f)


def makeCorpus(series):
    series = series.apply(lambda x : eval(x))
    dictionary = corpora.Dictionary(series)
    corpus = [dictionary.doc2bow(text) for text in series]
    return dictionary, corpus




if __name__ == '__main__':
    startLDA(ldaConfig['19~23세 탈모'])
    startLDA(ldaConfig['샴푸&영양제'])