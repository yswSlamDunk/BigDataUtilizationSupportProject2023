from requests_html import HTMLSession
import concurrent.futures
from multiprocessing import cpu_count
import csv
import sys
from math import ceil

s = HTMLSession()
payload = {
    'mb_id': 'dataflow28',
    'mb_password': 'flowdata2833!!'
}
p = s.post('https://daedamo.com/new/bbs/login.php', data=payload)
base_url = 'https://daedamo.com/note?overlaps=6&page='

def nav_small_page(posts):
    print('.',end='')
    sys.stdout.flush()
    r = s.get(posts[0])
    title = r.html.find('h1',first=True).text
    author = r.html.find('div.noneanonymousnick',first=True).find('a',first=True).text
    datetime = r.html.find('time',first=True).attrs['datetime']
    text = r.html.find('h3#view_content',first=True).text
    images = [img.attrs['src'] for img in r.html.find('h3#view_content',first=True).find('img.lazy')]
    views = r.html.find('div.hit.flex',first=True).text
    comments = []
    if len(posts) > 1:
        for post in posts[1:]:
            r = s.get(post)
            c_title = r.html.find('h1',first=True).text
            c_text = r.html.find('h3#view_content',first=True).text
            comments.append((c_title,c_text))
    return {
        'Title':title,
        'Author':author,
        'Date Posted':datetime,
        'Text':text,
        'Images':images,
        'Views':views,
        'Comments':comments
    }

def save_to_csv(lst):
    keys = ['Title','Author','Date Posted','Text','Images','Views','Comments']
    try:
        with open('good_talmo.csv','a',encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writerows(lst)
    except Exception as e:
        print('Unable to save CSV')
        print(e)

def nav_big_page():
    posts = []
    print('Gathering page links',end='')
    sys.stdout.flush()
    for page in range(1,11):
        print('.',end='')
        sys.stdout.flush()
        r = s.get(base_url + str(page))
        entries = r.html.find('div.list_wrap')
        for entry in entries:
            if not entry.find('span.i_reply_gray_16'):
                posts.append([entry.find('a.flex',first=True).attrs['href']])
            else:
                posts[-1].append(entry.find('a.flex',first=True).attrs['href'])
    print()
    print('Working',end='')
    sys.stdout.flush()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
        chunksize = ceil(len(posts)/(cpu_count() - 2))
        lst = [res for res in executor.map(nav_small_page,posts,chunksize=chunksize) if res is not None]
    save_to_csv(lst)

def init_dir():
    keys = ['Title','Author','Date Posted','Text','Images','Views','Comments']
    with open('good_talmo.csv','w',encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()

def main():
    init_dir()
    nav_big_page()
    
if __name__ == '__main__':
    main()