import os
import pandas as pd
import numpy as np
import re
from tqdm import tqdm

from kss import split_sentences
# from hanspell import spell_checker
from konlpy.tag import Okt

from multiprocessing import Pool

def tagging_sentence_old(sentence, okt):
    return okt.nouns(sentence)

def tagging_sentence(sentence, kkma):
    pos = kkma.pos(sentence)
    result = []

    for t in pos:
        if t[1] in ['NNG', 'NNP', 'VV', 'VA']:
            if t[1] == 'VV':
                result.append(t[0] + '다')
            else:
                result.append(t[0])

    return result

def splitSentence(sentence):
    result = []

    split_sentences_result = split_sentences(sentence)

    for sentence in split_sentences_result:
        if sentence[-1] not in [".", "!", "?"]:
            sentence = sentence + "."
            result.append(sentence)
        else:
            result.append(sentence)
    result = ' '.join(result)

    return result


def cleanStr(sentence):
    pattern = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)' # E-mail제거
    sentence = re.sub(pattern=pattern, repl='', string=sentence)
    pattern = '(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+' # URL제거
    sentence = re.sub(pattern=pattern, repl='', string=sentence)
    pattern = '([ㄱ-ㅎㅏ-ㅣ]+)'  # 한글 자음, 모음 제거
    sentence = re.sub(pattern=pattern, repl='', string=sentence)
    pattern = '<[^>]*>'         # HTML 태그 제거
    sentence = re.sub(pattern=pattern, repl='', string=sentence)
    sentence = re.sub('\n', '.', string=sentence)
    pattern = '[^\w\s\n.!?]'         # 특수기호제거
    sentence = re.sub(pattern=pattern, repl='', string=sentence)
    sentence = re.sub('[-=+,#/\:^$@*\"※~&%ㆍ』\\‘|\(\)\[\]\<\>`\'…》]','', string=sentence)

    return sentence 


def clean(sentence):
    # punct_mapping = {"‘": "'", "₹": "e", "´": "'", "°": "", "€": "e", "™": "tm", 
    #                  "√": " sqrt ", "×": "x", "²": "2", "—": "-", "–": "-", "’": "'", 
    #                  "_": "-", "`": "'", '“': '"', '”': '"', '“': '"', "£": "e", 
    #                  '∞': 'infinity', 'θ': 'theta', '÷': '/', 'α': 'alpha', '•': '.', 
    #                  'à': 'a', '−': '-', 'β': 'beta', '∅': '', '³': '3', 'π': 'pi'} 
    
    # punct = list(punct_mapping.keys())
    
    # for p in punct:
    #     sentence = sentence.replace(p, punct_mapping[p])

    # sentence = sentence.replace(u'\xa0', ' ').replace(u'\r', ' ')

    # for p in punct:
    #     sentence = sentence.replace(p, f' {p} ')
    
    # specials = {'\u200b': ' ', '…': ' ... ', '\ufeff': '', 'करना': '', 'है': ''}
    # for s in specials:
    #     sentence = sentence.replace(s, specials[s])

    return sentence.strip()


def preprocessingSentence(sentence, okt):
    try:
        sentence = clean(sentence)
        sentence = cleanStr(sentence)
        sentence = splitSentence(sentence)
        # sentence = spell_checker.check(sentence).checked
        result = tagging_sentence(sentence, okt)
        sentimentResult = np.nan
        return sentence, result, sentimentResult

    except:
        print(sentence)
        return 'error', 'error', 'error'
    

def savePreprocessingSentence(input):
    # 여기에선, df_split의 요소들을 input으로 받음
    df = input[0]
    config = input[1]
    okt = Okt()

    for i, row in tqdm(df.iterrows()):
        try:
            sentence, result, sentimentResult = preprocessingSentence(row[config['additionalColumns'][0]], okt)
        except:
            continue
        addDataFrame = pd.DataFrame({config['additionalColumns'][1]: sentence,
                                    config['additionalColumns'][2]: [result],
                                    config['additionalColumns'][3]: sentimentResult},
                                    index = [i])
        concat_df = row.to_frame().T
        concat_df = concat_df.reindex([i])
        pd.concat([concat_df, addDataFrame], axis = 1, ignore_index = True).to_csv(config['outputPath'], 
                                                                                    index = False,
                                                                                    header = False,
                                                                                    mode = 'a',
                                                                                    encoding = 'utf-8-sig',
                                                                                    escapechar = '\\')

def parallelPreprocessing(config, n_cores = 4): 
    # 입력되는 데이터의 예시: confing['19~23세 탈모']
    df = pd.read_csv(config['inputPath'])
    df['date'] = pd.to_datetime(df['date'])

    condition_date = df['date'] > '2020'

    df = df[condition_date]
    df['sub-title'] = df['sub-title'].fillna('')
    df['totalComment'] = df['title'] + df['sub-title'] + df['text']
    
    if not os.path.isfile(config['outputPath']):
        pd.DataFrame(columns = list(df.columns) + config['additionalColumns'][1:]).to_csv(config['outputPath'] , 
                                                                                          header = True, 
                                                                                          index = False,
                                                                                          encoding = 'utf-8-sig',
                                                                                          escapechar = '\\')
    df_split = np.array_split(df, n_cores)

    pool = Pool(processes = n_cores)
    pool.map(savePreprocessingSentence, zip(df_split, [config] * n_cores))
    pool.close()
    pool.join()

if __name__ == '__main__':
    config = {'additionalColumns' : ['totalComment', 'preprocessedSentence', 'keyword', 'sentimentResult'],
              'inputPath' : '../Data/Preprocessed/조경뉴스.csv',
              'outputPath' : '../Data/Preprocessed/조경뉴스_keywords.csv'}
    
    parallelPreprocessing(config)