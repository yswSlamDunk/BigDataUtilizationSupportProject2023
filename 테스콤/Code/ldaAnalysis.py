import os
import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm

import gensim
from gensim import corpora

def startLDA(df, ldaConfig):
    series = df[ldaConfig['keywordColumn']]
    dictionary, corpus = makeCorpus(series)

    for numTopic in tqdm(ldaConfig['numTopics']):
        ldaModel = gensim.models.ldamodel.LdaModel(corpus, num_topics = numTopic,
                                                   id2word = dictionary, passes = 5)
        with open(ldaConfig['outputPath'] + f'topicNum_{str(numTopic)}.pickle', 'wb') as f:
            pickle.dump((ldaModel, dictionary, corpus), f)


def makeCorpus(series):
    # series = series.apply(lambda x : eval(x))
    dictionary = corpora.Dictionary(series)
    corpus = [dictionary.doc2bow(text) for text in series]
    return dictionary, corpus


def retutnTopic(df, ldaConfig):
    with open(ldaConfig['resultPath'], 'rb') as f:
        ldaModel, dictionary, corpus = pickle.load(f)

        topic_table = make_topictable_per_doc(ldaModel, corpus)
        df = df.reindex(range(len(df)))
        topic_table = topic_table.reindex(range(len(topic_table)))

        df = pd.concat([df, topic_table], axis = 1)

        df.to_csv(ldaConfig['inputPath'] , index = False)

def make_topictable_per_doc(ldamodel, corpus):
    topic_table = pd.DataFrame(columns = ['propTopic', 'propTopicRatio', 'topicsRatio'])

    for i, topic_list in enumerate(ldamodel[corpus]):
        doc = topic_list[0] if ldamodel.per_word_topics else topic_list            
        doc = sorted(doc, key=lambda x: (x[1]), reverse=True)
        
        for j, (topic_num, prop_topic) in enumerate(doc): 
            if j == 0:
                topic_table = pd.concat([topic_table, pd.DataFrame({'propTopic': [int(topic_num)],
                                                                    'propTopicRatio': [round(prop_topic, 4)],
                                                                    'topicsRatio' : [topic_list]})],
                                        axis = 0,
                                        ignore_index = True)
            else:
                break
    return topic_table