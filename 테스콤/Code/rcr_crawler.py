from requests_html import HTMLSession
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
import csv
import pandas as pd
from tqdm import tqdm

s = HTMLSession()

def get_response(url):
    try:
        r = s.get(url)
    except:
        return
    if r.status_code // 100 == 2:
        return r
    print('bad response:',r.status_code)
    print(url)
    return

def get_urls(base_url):
    urls = []
    r = get_response(base_url)
    if r:
        article_lst = r.html.find('div#tdi_80',first=True)
        titles = article_lst.find('h3.entry-title')
        for title in titles:
            url = str(title.find('a',first=True).attrs['href'])
            if (url.startswith('https://www.rcrwireless.com') or url.startswith('http://www.rcrwireless.com')) and ('rcrtv' not in url):
                urls.append(title.find('a',first=True).attrs['href'])
        return urls
    return

# Try/Except block on paragraphs to filter out URLs with no text
# Other Try/Except blocks used for debugging purposes
def crawl_page(it):
    r = get_response(it[0])
    if r:
        res = dict.fromkeys(['Title','Author','Date','Text','Keywords','Href','Category'])
        try:
            paragraphs = r.html.find('div.td_block_wrap.tdb_single_content',first=True).find('p')
        except AttributeError:
            print(f'Paragraphs: {it[0]}')
            return
        else:
            res['Text'] = ' '.join([p.text for p in paragraphs])
        try:
            res['Title'] = r.html.find('h1.tdb-title-text',first=True).text
        except AttributeError:
            print(f'Title: {it[0]}')
        try:
            res['Author'] = r.html.find('a.tdb-author-name',first=True).text
        except AttributeError:
            print(f'Author: {it[0]}')
        try:
            res['Date'] = r.html.find('time.entry-date',first=True).attrs['datetime']
        except AttributeError:
            print(f'Date: {it[0]}')
        try:
            kw = r.html.find('div.tdb-category.td-fix-index',first=True).find('a')
        except AttributeError:
            print(f'Keywords: {it[0]}')
        else:
            res['Keywords'] = [word.text for word in kw]
        res['Href'] = it[0]
        res['Category'] = it[1]
        return res
    return

def save_urls(urls):
    df = pd.DataFrame(columns=['URL','Category'])
    df['URL'] = urls.keys()
    df['Category'] = urls.values()
    df.to_csv('urls.csv',encoding='utf-8-sig',index=False,escapechar='\\')

def save_csv(info):
    keys = ['Title','Author','Date','Text','Keywords','Href','Category']
    try:
        with open('rc.csv','w',encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writeheader()
            dict_writer.writerows(info)
    except Exception as e:
        print('Unable to save as CSV')
        print(e)
    

def main():
    urls = dict()
    root_url = 'https://www.rcrwireless.com/page/'
    search_words = [('?s=6G',36),('?s=MIMO',58),('?s=6E',26),('?s=Automotive',82)]
    for word in search_words:
        cat = word[0][3:]
        with ProcessPoolExecutor(max_workers=cpu_count()-3) as executor:
            res = executor.map(get_urls,[root_url+str(i)+word[0] for i in range(1,word[1]+1)])
            for lst in tqdm(res):
                for url in lst:
                    if url not in urls.keys():
                        urls[url] = [cat]
                    else:
                        urls[url].append(cat)
    print('Collected all URLs')
   
   # Save gathered URLs to DataFrame
    save_urls(urls)

    # Gather information from each URL
    lst = []
    with ProcessPoolExecutor(max_workers=cpu_count()-3) as executor:
        for res in executor.map(crawl_page,list(urls.items())):
            if res:
                lst.append(res)

    # Save gathered information to a CSV file
    save_csv(lst)

if __name__ == '__main__':
    main()
    # Gather URLs
   
