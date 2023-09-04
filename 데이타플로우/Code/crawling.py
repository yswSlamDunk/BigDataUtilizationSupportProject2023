import os
import pandas as pd
import numpy as np

import time
from tqdm.auto import tqdm
import multiprocessing

import requests
from bs4 import BeautifulSoup

path_save = '샴푸&두피케어_체험평가단.csv'
path_save_base = '../Data/Raw'
save_path = os.path.join(path_save_base, path_save)
fieldNames = ['title', 'category', 'date', 'writer', 'rank', 'view', 'href', 'content', 'imageList']

def clawringContentImage(href):
    response = requests.get(href)
    
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        res = soup.find('h3', {'id' : 'view_content'})
        try:
            content = res.text
        except:
            return np.nan, []
        
        images = res.find_all('img', {'class' : 'lazy content-image'})

        if images != []:
            imageList = [url['data-original'] for url in res.find_all('img', {'class' : 'lazy content-image'})]
        else:
            imageList = []
        return content, imageList
    
    else:
        return np.nan, []    
    
def parsing_save(re):
    re = BeautifulSoup(re, 'html.parser')
    category = re.find('a', {'class' : 'mw_basic_list_category'}).text
    date = re.find('div', {'class' : 'mw_basic_list_datetime media-no-text'}).text
    view = re.find('div', {'class' : 'mw_basic_list_hit media-no-text'}).text
    title = re.find('h3', {'class' : 'media-list-subject flex'}).text.replace('\n', '')
    rank = str(re.find('img')['src']).split('/')[-1].split('.')[0]
    href = re.find_all('a')[1]['href']

    try:
        writer = re.find('a', {'class' : 'sv_member'}).text.strip()
    except:
        writer = re.find('div', {'mw_basic_list_name media-no-text'}).text

    content, imageList = clawringContentImage(href)

    try:
        pd.DataFrame({'title' : [title],
                      'category' : [category],
                      'date' : [date],
                      'writer' : [writer],
                      'rank' : [rank],
                      'view' : [view],
                      'href' : [href],
                      'content' : [content.strip()],
                      'imageList' : [imageList]}).to_csv(save_path,
                                                         mode = 'a',
                                                         index = False,
                                                         header = False,
                                                         encoding = 'utf-8-sig')
    except:
        print({'title' : title,
                'category' : category,
                'date' : date,
                'writer' : writer,
                'rank' : rank,
                'view' : view,
                'href' : href,
                'content' : content,
                'imageList' : imageList})
        print(href, ': Error', '\n')
        print('==================================================================')

def clawringHref01(url, pageNum, startPage = 1):
    if not os.path.isfile(save_path):
        tmp = pd.DataFrame(columns = fieldNames)
        tmp.to_csv(save_path, index = False, encoding = 'utf-8-sig', header=fieldNames)

    for page in tqdm(range(startPage, pageNum + 1)):
        page = str(page)
        for _ in range(3):
            try:
                response = requests.get(url + page)
                if response.status_code == 200:
                    html = response.text
                    soup = BeautifulSoup(html, 'html.parser')
                    re_list = soup.find_all('div', {"class" : "list_wrap flex_spbtw"})
                    re_list = [str(re) for re in re_list]
                    with multiprocessing.Pool(multiprocessing.cpu_count() -2) as p:
                        p.map(parsing_save, re_list)
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(5)


def clawringHref02(url, pageNum, startPage = 1):
    if not os.path.isfile(save_path):
        tmp = pd.DataFrame(columns = fieldNames)
        tmp.to_csv(save_path, index = False, encoding = 'utf-8-sig', header=fieldNames)

    for page in tqdm(range(startPage, pageNum + 1)):
        page = str(page)
        for _ in range(3):
            try:
                response = requests.get(url + page)

                if response.status_code == 200:
                    html = response.text
                    soup = BeautifulSoup(html, 'html.parser')
                    re_list = soup.find_all('div', {"class" : ["list_wrap", "flex_spbtw"]})
                    notice_list = soup.find_all('div', {'class' : ['notice_wrap']})
                    
                    if page == '1':
                        re_list = re_list[len(notice_list):]
                    re_list = [str(re) for re in re_list]
                    with multiprocessing.Pool(multiprocessing.cpu_count() -2) as p:
                        p.map(parsing_save, re_list)
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(5)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    path_save_base = '../Data/Raw'
    fieldNames = ['title', 'category', 'date', 'writer', 'rank', 'view', 'href', 'content', 'imageList']

    # path_save = '탈모톡톡_탈모수다.csv'
    # save_path = os.path.join(path_save_base, path_save)
    # url = 'https://daedamo.com/story?overlaps=1&page='
    # pageNum = 1500
    # startPage = 1019
    # clawringHref01(url, pageNum, startPage)

    # path_save = '샴푸&두피케어_샴푸&영양제.csv'
    # save_path = os.path.join(path_save_base, path_save)
    # url = 'https://daedamo.com/balmo?overlaps=1&page='
    # pageNum = 120
    # clawringHref01(url, pageNum)

    # path_save = '탈모톡톡_19~23세탈모.csv'
    # save_path = os.path.join(path_save_base, path_save)
    # url = 'https://daedamo.com/1923club?overlaps=1&page='
    # pageNum = 356
    # clawringHref01(url, pageNum)

    path_save = '샴푸&두피케어_체험평가단.csv'
    save_path = os.path.join(path_save_base, path_save)
    url = 'https://daedamo.com/job?overlaps=5&page='
    pageNum = 39
    clawringHref02(url, pageNum)