import os
import pandas as pd
import numpy as np

import csv
from tqdm.auto import tqdm
import multiprocessing

import requests
from bs4 import BeautifulSoup

path_save = 'href_탈모톡톡_탈모수다.csv'
path_save_base = '../Data'
save_path = os.path.join(path_save_base, path_save)
fieldNames = ['title', 'category', 'date', 'writer', 'rank', 'view', 'href', 'content', 'imageList']

def clawringContentImage(href):
    response = requests.get(href)
    
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        res = soup.find('h3', {'id' : 'view_content'})
        content = res.text
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

    with open(save_path, 'a', newline = '') as csvfile:
        csvWriter = csv.DictWriter(csvfile, fieldnames = fieldNames)
        
        try:
            csvWriter.writerow({'title' : title,
                                'category' : category,
                                'date' : date,
                                'writer' : writer,
                                'rank' : rank,
                                'view' : view,
                                'href' : href,
                                'content' : content,
                                'imageList' : imageList})      
        except:
            print(href, ': Error')

def clawringHref01(url, pageNum, startPage = 1):
    if not os.path.isfile(save_path):
        tmp = pd.DataFrame(columns = fieldNames)
        tmp.to_csv(save_path, index = False)
        
        with open(save_path, 'w', newline = '') as csvfile:
            csvWriter = csv.DictWriter(csvfile, fieldnames = fieldNames)
            csvWriter.writeheader()

    for page in tqdm(range(startPage, pageNum + 1)):
        page = str(page)
        response = requests.get(url + page)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            re_list = soup.find_all('div', {"class":"list_wrap flex_spbtw"})
            re_list = [str(re) for re in re_list]
    
            with multiprocessing.Pool(multiprocessing.cpu_count() -2) as p:
                p.map(parsing_save, re_list)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    path_save_base = '../Data'
    fieldNames = ['title', 'category', 'date', 'writer', 'rank', 'view', 'href', 'content', 'imageList']

    path_save = 'href_탈모톡톡_탈모수다.csv'
    save_path = os.path.join(path_save_base, path_save)
    url = 'https://daedamo.com/story?overlaps=1&page='
    pageNum = 1000
    clawringHref01(url, pageNum)

    path_save = 'href_탈모톡톡_샴푸&영양제.csv'
    save_path = os.path.join(path_save_base, path_save)
    url = 'https://daedamo.com/balmo?overlaps=1&page='
    pageNum = 120
    clawringHref01(url, pageNum)