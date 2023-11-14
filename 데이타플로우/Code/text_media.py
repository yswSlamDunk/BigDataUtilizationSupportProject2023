from requests_html import HTMLSession
import csv
import sys
import concurrent.futures
from multiprocessing import cpu_count
from math import ceil
import os
from datetime import datetime

s = HTMLSession()
base_urls = ['https://daedamo.com/forum?overlaps=1&page=','https://daedamo.com/story?overlaps=1&page=','https://daedamo.com/balmo?overlaps=5&page=','https://daedamo.com/job?overlaps=5&page=']

def get_response(base_url,page=0):
    if page == 0:
        url = base_url
    else:
        url = base_url+str(page)
    r = s.get(url)
    r_error_handler(r,url)
    return r

def r_error_handler(r,url):
    if r.status_code != 200:
        print("URL:",url)
        print("URL Status Code:",r.status_code)

def parse_subject(subject):
    if len(subject) == 1:
        cat = 'n/a'
        title = subject[0][1:].strip()
    else:
        cat = subject[0][1:].strip()
        title = subject[1][1:].strip()
    return cat,title

def parse_top_box(left,right):
    nickname = left.find('div.nickname',first=True)
    if nickname.find('a',first=True):
        author = nickname.find('a',first=True).text.strip()
    else:
        if nickname.text.strip():
            author = nickname.text.strip()
        else:
            print('cant find post author')
            author = 'n/a'

    datetime = left.find('time',first=True).attrs['datetime']
    views = left.find('div.hit',first=True).find('div')[2].text.strip()
    comments = right.find('div.comment',first=True).text.strip()
    return author,datetime,views,comments

def parse_info(r):
    subject = r.html.find('div.view_subject_box',first=True).find('h1',first=True).text.strip()         
    subject = subject.split(']')
    cat,title = parse_subject(subject)
    top_box = r.html.find('div.view_info_top_box',first=True)
    author,datetime,views,comm_count = parse_top_box(top_box.find('div.left',first=True),top_box.find('div.right',first=True))
    return cat,title,author,datetime,views,comm_count

def parse_images(images):
    if images:
        all_imgs = []
        for img in images:
            all_imgs.append(img.attrs['data-original'])
        return all_imgs
    else:
        return ['n/a']

def parse_content(r):
    content = r.html.find('h3#view_content',first=True)
    if content.text.strip():
        text = content.text.strip()
    else:
        text = 'n/a'
    images = content.find('img.content-image')
    images = parse_images(images)
    return text,images

def parse_comment(comment):
    author_box = comment.find('div.noneanonymousnick',first=True)
    if author_box.find('a'):
        author = author_box.find('a',first=True).text.strip()
    elif author_box.text.strip():
        author = author_box.text.strip()
    else:
        print('cant find the author')
        author = 'n/a'   
    time = comment.find('span.mw_basic_comment_datetime',first=True).find('span')[2].attrs['title']
    content = comment.find('div.contents',first=True)
    if content:
        if content.find('span.level_block'):
            content = '(level blocked)'
        elif content.text.strip():
            content = content.text.strip()
        else:
            print('cant find content')
            content = 'n/a'
    else:
        content = 'n/a'
    return {
        'Author':author,
        'Time':time,
        'Content':content
    }

def parse_comments(r):
    comments = r.html.find('div.view_comment_list')
    if comments:
        all_comments = []
        for comment in comments:
            all_comments.append(parse_comment(comment))
        return all_comments
    else:
        return ['n/a']

# def make_dict(info,text,images,comments):
def make_dict(info,text,images,url):
    return {
        'Title':info[1],
        'DateTime':info[3],
        'Author':info[2],
        'Category':info[0],
        'Text':text,
        'Images':'\n'.join(images),
        # 'Comments':'\n'.join([str(comment) for comment in comments]),
        # 'Comment Count':info[5],
        'Views':info[4],
        'URL':url
    }

def parse(r):
    if not r.html.find('body') or not r.html.find('div#mw_basic'):
        return {
            'Title':'n/a',
        'DateTime':'n/a',
        'Author':'n/a',
        'Category':'n/a',
        'Text':'n/a',
        'Images':'n/a',
        # 'Comments':'n/a',
        # 'Comment Count':'n/a',
        'Views':'n/a',
        'URL':'n/a'
        }
    try:
        info = parse_info(r) # category,title,author,date,views,comments
    except Exception as e:
        print(1)
        raise e
    try:
        text,images = parse_content(r)
    except Exception as e:
        print(2)
        raise e
    url = r.url
    # comments = parse_comments(r)
    # return make_dict(info,text,images,comments)
    return make_dict(info,text,images,url)

def nav_art_page(url):
    print('.',end='')
    sys.stdout.flush()
    r = get_response(url)
    info = parse(r)
    return info

def save_to_csv(info,page=None):
    # keys = ['Title','DateTime','Author','Category','Text','Images','Comments','Comment Count','Views']
    keys = ['Title','DateTime','Author','Category','Text','Images','Views','URL']
    try:
        with open(f'./text-media-crawler/text_media{page + 1}.csv','a',encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writerows(info)
    except Exception as e:
        print('Unable to save as CSV')
        print(e)
    
def nav_one(idx,page_start = 1,page_end = 101):
    refresh_directory(idx)
    lst = []
    for page in range(page_start,page_end):
        r = get_response(base_urls[idx],page)
        print(f'Page {page}...',end='')
        sys.stdout.flush()
        articles = r.html.find('div.list_box')
        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
            chunksize = ceil(len(articles)/(cpu_count() - 2))
            for res in executor.map(nav_art_page,[article.find('div.subject',first=True).find('a',first=True).attrs['href'] for article in articles], chunksize=chunksize):
                if res['Title'] != 'n/a':
                    lst.append(res)
        save_to_csv(lst,idx)
        print()
    return

def nav_two(idx,page_start = 1,page_end = 101):
    refresh_directory(idx)
    lst = []
    for page in range(page_start,page_end):
        r = get_response(base_urls[idx],page)
        print(f'Page {page}...',end='')
        sys.stdout.flush()
        articles = r.html.find('div.list_wrap')
        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
            chunksize = ceil(len(articles)/(cpu_count() - 2))
            for res in executor.map(nav_art_page,[article.find('div.mw_basic_list_subject',first=True).find('a')[1].attrs['href'] for article in articles], chunksize=chunksize):
                if res['Title'] != 'n/a':
                    lst.append(res)
        save_to_csv(lst,idx)
        print()
    return

def nav_three(idx,page_start = 1,page_end = 101):
    refresh_directory(idx)
    lst = []
    for page in range(page_start,page_end):
        r = get_response(base_urls[idx],page)
        print(f'Page {page}...',end='')
        sys.stdout.flush()
        products = r.html.find('bbs_list_box')
        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
            chunksize = ceil(len(products)/(cpu_count() - 2))
            for res in executor.map(nav_art_page,[product.find('div.mw_basic_list_subject',first=True).find('a')[1].attrs['href'] for product in products], chunksize=chunksize):
                if res['Title'] != 'n/a':
                    lst.append(res)
        save_to_csv(lst,idx)
        print()

    return

def refresh_directory(idx):
    print(os.getcwd())
    for f in os.listdir(f'{os.getcwd()}'):
        if f.endswith(f'{idx+1}.csv'):
            os.remove(os.path.join(f'{os.getcwd()}',f))

    # keys = ['Title','DateTime','Author','Category','Text','Images','Comments','Comment Count','Views']
    keys = ['Title','DateTime','Author','Category','Text','Images','Views','URL']
    with open(f'./text_media{idx+1}.csv','w',encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()

def main():
    # 탈모톡톡
    # nav_one(0,1,1001)
    # 탈모수다
    # nav_two(1,1,1001)
    # 샴푸&영양제
    # nav_two(2,1,151)
    # 체험평가단
    nav_two(3,1,11)
    # 탈모샴푸 찾기
    # 체험평가단
    # 탈모치료성공스토리



if __name__ == '__main__':
    main()