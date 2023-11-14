import os
import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

import gensim
from gensim import corpora

from .config import *

def startLDA(ldaConfig):
    if ldaConfig['isLdaColumns'] == False:
        df = pd.read_excel(ldaConfig['inputPath'])
        series = df[ldaConfig['keywordColumn']]
        dictionary, corpus = makeCorpus(series)

        for numTopic in tqdm(ldaConfig['numTopics']):
            ldaModel = gensim.models.ldamodel.LdaModel(corpus, num_topics = numTopic,
                                                       id2word = dictionary, passes = 15)
            with open(ldaConfig['outputPath'] + f'topicNum_{str(numTopic)}.pickle', 'wb') as f:
                pickle.dump((ldaModel, dictionary, corpus), f)

    else:
        df = pd.read_csv(ldaConfig['inputPath'])
        condition = df[ldaConfig['keywordColumn']] != '[]'
        df = df[condition].drop_duplicates()

        for column in df['category'].unique():
            condition = df['category'] == column
            tmp_df = df[condition]

            series = tmp_df[ldaConfig['keywordColumn']]
            dictionary, corpus = makeCorpus(series)

            for numTopic in tqdm(ldaConfig['numTopics']):
                ldaModel = ldaModel = gensim.models.ldamodel.LdaModel(corpus, num_topics = numTopic,
                                                                      id2word = dictionary, passes = 15)
                with open(os.path.join(ldaConfig['outputPath'], f'{column}', f'topicNum_{str(numTopic)}.pickle'), 'wb') as f:
                    pickle.dump((ldaModel, dictionary, corpus), f)

    


def makeCorpus(series):
    series = series.apply(lambda x : eval(x))
    dictionary = corpora.Dictionary(series)
    corpus = [dictionary.doc2bow(text) for text in series]
    return dictionary, corpus


def returnTopic(ldaConfig):
    if ldaConfig['isLdaColumns'] == False:
        df = pd.read_excel(ldaConfig['inputPath'])

        with open(ldaConfig['ResultPath'], 'rb') as f:
            ldaModel, dictionary, corpus = pickle.load(f)

            topic_table = make_topictable_per_doc(ldaModel, corpus)
            df = df.reindex(range(len(df)))
            topic_table = topic_table.reindex(range(len(topic_table)))

            df = pd.concat([df, topic_table], axis = 1)

            df.to_excel(ldaConfig['inputPath'] , index = False)
    
    else:
        df = pd.read_csv(ldaConfig['inputPath'])
        condition = df[ldaConfig['keywordColumn']] != '[]'
        df = df[condition].drop_duplicates()

        for column in sorted(df['category'].unique()):
            condition = df['category'] == column
            tmp_df = df[condition]

            with open(ldaConfig['ResultPath'][column], 'rb') as f:
                ldaModel, dictionary, corpus = pickle.load(f)

                topic_table = make_topictable_per_doc(ldaModel, corpus)
                tmp_df.index = range(len(tmp_df))
                topic_table.index = range(len(tmp_df))

                tmp_df = pd.concat([tmp_df, topic_table], axis = 1)

                tmp_df.to_csv(os.path.join(ldaConfig['topicPath'], column + '.csv'),
                              index = False,
                              encoding = 'utf-8-sig',
                              escapechar = '\\')
                        

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


def painPointCluster(ldaConfig, returnPainPoint = False):
    if 'fileFormat' in ldaConfig.keys():
        df = pd.read_csv(ldaConfig['inputPath'])
    else:
        df = pd.read_excel(ldaConfig['inputPath'])
    df['topicsRatio'] = df['topicsRatio'].apply(lambda x : eval(x))
    tmp_df = df[['href', 'propTopic', 'topicsRatio']]
    topicList = sorted(tmp_df['propTopic'].unique())
    result_df = pd.DataFrame()

    for l, propTopic in enumerate(topicList):
        df_kmeans = pd.DataFrame(columns = [str(i) for i in topicList])
        tmp = tmp_df[tmp_df['propTopic'] == propTopic]

        for i, row in tmp.iterrows():
            tmp_dict = {}
            
            for j in row['topicsRatio']:
                tmp_dict[str(j[0])] = [j[1]]
            
            df_kmeans = pd.concat([df_kmeans, pd.DataFrame(tmp_dict)],
                                  axis = 0, ignore_index = True)
        
        df_kmeans = df_kmeans.fillna(0)
        
        if returnPainPoint == False:
            distortions = []
            K = range(1, 16)
            for n_cluster in K:
                model = KMeans(n_clusters = n_cluster, random_state = 1234)
                model.fit(df_kmeans)
                distortions.append(model.inertia_)

            plt.figure(figsize = (10, 10))
            plt.plot(K, distortions, 'bx-')
            plt.xlabel('Values of K')
            plt.ylabel('Inertia')
            plt.title('The Elbow Method using Inertia')
            plt.savefig(os.path.join(ldaConfig['kmeansPath'], f'knnResult_{propTopic}.png'))

        else:
            model = KMeans(n_clusters = ldaConfig['knn'][l], random_state = 1234)
            y_pred = model.fit_predict(df_kmeans)
            tmp.loc[:, 'cluster'] = y_pred
            result_df = pd.concat([result_df, tmp],
                                   axis = 0,
                                   ignore_index = True)
    
    if returnPainPoint == True:
        if 'fileFormat' in ldaConfig.keys():
            df.merge(result_df[['href', 'cluster']],
                     on  = ['href'],
                     how = 'left').to_csv(ldaConfig['inputPath'], index = False)
        else:        
            df.merge(result_df[['href', 'cluster']],
                    on = ['href'],
                    how = 'left').to_excel(ldaConfig['inputPath'], index = False)


def topicTrend(ldaConfig, unit = 'Y', startDate = False):
    df = pd.read_excel(ldaConfig['inputPath'])
    df['date'] = df['date'].apply(lambda x : pd.to_datetime(x))
    df.set_index('date', inplace = True)

    if startDate != False:
        df = df[startDate:]

    tmp = df.groupby(['propTopic']).resample(unit)['href'].count().reset_index()

    fig, ax = plt.subplots(figsize = (10, 10))
    for propTopic in sorted(tmp['propTopic'].unique()):
        tmp_df = tmp[tmp['propTopic'] == propTopic]

        ax.plot(tmp_df['date'], tmp_df['href'],
                 label = f'propTopic: {propTopic}')
        ax.legend()
        fig.savefig(os.path.join(ldaConfig['topicTrendPath'], 'topicTrend.png'))

    total_tmp = df.resample(unit)['href'].count().reset_index()

    for propTopic in sorted(tmp['propTopic'].unique()):
        fig, ax = plt.subplots(figsize = (10, 10))
        tmp_df = tmp[tmp['propTopic'] == propTopic]
        ax.plot(tmp_df['date'], tmp_df['href'],
                color = 'blue', 
                label = f'propTopic: {propTopic}')
        ax.tick_params(axis = 'y', labelcolor = 'blue')

        ax_twin = ax.twinx()
        ax_twin.plot(total_tmp['date'], total_tmp['href'],
                     color = 'red',
                     label = 'total')
        
        fig.savefig(os.path.join(ldaConfig['topicTrendPath'], f'topicTrend_{propTopic}.png'))


if __name__ == '__main__':
    # startLDA(ldaConfig['19~23세 탈모'])
    # startLDA(ldaConfig['샴푸&영양제'])
    # startLDA(ldaConfig['탈모수다'])
    # startLDA(ldaConfig['샴푸&두피제품 찾기'])
    # returnTopic(ldaConfig['19~23세 탈모'])
    # returnTopic(ldaConfig['샴푸&영양제'])
    # returnTopic(ldaConfig['탈모수다'])
    returnTopic(ldaConfig['샴푸&두피제품 찾기'])
    # painPointCluster(ldaConfig['19~23세 탈모'])
    # painPointCluster(ldaConfig['샴푸&영양제'])
    # painPointCluster(ldaConfig['탈모수다'])
    # painPointCluster(ldaConfig['19~23세 탈모'], True)
    # painPointCluster(ldaConfig['샴푸&영양제'], True)
    # painPointCluster(ldaConfig['탈모수다'], True)
    # topicTrend(ldaConfig['탈모수다'], unit = 'Q', startDate = '2019')
    # topicTrend(ldaConfig['19~23세 탈모'])
    # topicTrend(ldaConfig['샴푸&영양제'])

    print('Hello World')

