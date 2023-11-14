from requests_html import HTMLSession
import sys
import concurrent.futures
from math import ceil
from multiprocessing import cpu_count
import csv

s = HTMLSession()
base_url = 'https://daedamo.com/job?overlaps=5&page='

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

def save_to_csv(lst):
    keys = ['Title','Author','Date Posted','Text','Views','Comments']
    try:
        with open('good_talmo.csv','w',encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writeheader(keys)
            dict_writer.writerows(lst)
    except Exception as e:
        print('Unable to save CSV')
        print(e)

def parse_title(r):
    whole = r.html.find('h1',first=True).text.split(']')
    if len(whole) == 1:
        return 'n/a',whole[0]
    else:
        return whole[0][1:],whole[1][1:]

def parse_header(r):
    author = r.html.find('div.noneanonymousnick',first=True).find('a',first=True).text
    datetime = r.html.find('time',first=True).attrs['datetime']
    views = r.html.find('div.hit.flex',first=True).text
    return author,datetime,views



def nav_small_page(link):
    print('.',end='')
    sys.stdout.flush()
    r = get_response(link)
    cat,title = parse_title(r)
    author,datetime,views = parse_header(r)
    text,images = parse_content(r)


def nav_big_page():
    links = []
    print('Gathering pages',end='')
    sys.stdout.flush()
    for page in range(1,11):
        print('.',end='')
        sys.stdout.flush()
        r = get_response(base_url= + str(page))
        entries = r.html.find('div.list_wrap')
        for entry in entries:
            links.append([entry.find('a.flex',first=True).attrs['href']])
    print()
    print('Working',end='')
    sys.stdout.flush()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
        chunksize = ceil(len(links)/(cpu_count() - 2))
        lst = [res for res in executor.map(nav_small_page,links,chunksize=chunksize) if res is not None]
    save_to_csv(lst)
        

def main():
    nav_big_page()
    return

if __name__ == '__main__':
    main()