from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import concurrent.futures
import random as r
from datetime import datetime
import pandas as pd
import numpy as np
import sys

# base_urls is a list of each URL to parse in the format (title,url,end_page)
base_urls = [('가드닝',"https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.menuid=1247%26userDisplay=50%26search.boardtype=L%26search.specialmenutype=%26search.totalCount=408%26search.cafeId=15158977%26search.page=",9),('병충해','https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.menuid=1185%26userDisplay=50%26search.boardtype=L%26search.specialmenutype=%26search.totalCount=842%26search.cafeId=15158977%26search.page=',17),('식물이름','https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.menuid=1061%26userDisplay=50%26search.boardtype=L%26search.specialmenutype=%26search.totalCount=501%26search.cafeId=15158977%26search.page=',150),('조경설계','https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.boardtype=L%26search.menuid=1186%26search.marketBoardTab=D%26search.specialmenutype=%26userDisplay=50',8),('조경업무','https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.menuid=73%26userDisplay=50%26search.boardtype=L%26search.specialmenutype=%26search.totalCount=186%26search.cafeId=15158977%26search.page=',4),('조경시공','https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.menuid=1060%26userDisplay=50%26search.boardtype=L%26search.specialmenutype=%26search.totalCount=501%26search.cafeId=15158977%26search.page=',30),('조경관리','https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.menuid=1062%26userDisplay=50%26search.boardtype=L%26search.specialmenutype=%26search.totalCount=501%26search.cafeId=15158977%26search.page=',18),('취업/진로','https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.menuid=1090%26userDisplay=50%26search.boardtype=L%26search.specialmenutype=%26search.totalCount=501%26search.cafeId=15158977%26search.page=',30)]
# base_urls = [('취업진로','https://cafe.naver.com/teamsis?iframe_url=/ArticleList.nhn%3Fsearch.clubid=15158977%26search.menuid=1090%26userDisplay=50%26search.boardtype=L%26search.specialmenutype=%26search.totalCount=501%26search.cafeId=15158977%26search.page=',50)]

# Settings for Selenium Driver
opp = Options()
opp.add_argument('--no-sandbox')
opp.add_argument('--disabled-dev-shm-usage')
opp.add_argument('--blink-settings=imagesEnabled=false')
driver = webdriver.Chrome(options=opp)  # You can use other drivers as well (e.g., Firefox)

# Login to Naver
def login(user,pw):
    driver.get('https://nid.naver.com/nidlogin.login')
    driver.implicitly_wait(1 + (0.1 * r.randint(5,10)))
    driver.find_element('id','id').send_keys(user)
    driver.find_element('id','pw').send_keys(pw)
    driver.find_element('id','log.login').click()
    driver.implicitly_wait(1.5 + (0.1 * r.randrange(1,10)))
    print(driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[3]/div[1]/p[1]/img').get_attribute('src'))
    WebDriverWait(driver,60).until_not(EC.presence_of_element_located((By.CSS_SELECTOR,'#container > div > div.login_wrap.global')))
    
# Set up the page to be scraped
def init_page(url):
    driver.get(url)
    driver.implicitly_wait(1 + (0.1 * r.randint(5,10)))
    iframe = driver.find_element('id','cafe_main')
    driver.switch_to.frame(iframe)
    driver.implicitly_wait(2 + (0.1 * r.randint(5,10)))

# Gather URLs available on page
# Return list of URL links
def gather_links():
    articles = driver.find_elements(By.CLASS_NAME,'article-board')[1].find_elements(By.TAG_NAME,'tr')
    links = []
    for article in articles[::2]:
        article_number = article.find_element(By.CLASS_NAME,'inner_number').text
        article_href = article.find_element(By.CLASS_NAME,'inner_list').find_element(By.CLASS_NAME,'article').get_attribute('href')
        links.append((article_number,article_href))
    return links

# Gather the comments on each article page
# Return the author, datetime, and text of comment in a list
def gather_comment_info(comment):
    try:
        author = comment.find_element(By.CLASS_NAME,'comment_nickname').text
        post_datetime = datetime.strptime(comment.find_element(By.CLASS_NAME,'comment_info_date').text,'%Y.%m.%d. %H:%M')
        text = comment.find_element(By.CLASS_NAME,'text_comment').text
        return [author,post_datetime,text]
    except Exception as e:
        print('Failed to add comment')
        print(e)
        sys.stdout.flush()

# Convert the list of comments into a DataFrame
def make_comment(comments):
    df = pd.DataFrame(comments,columns=['Comment Author','Comment Timestamp','Comment Text'])
    return df

# Gather information from each article
# Return title, author, timestamp, text, image hrefs, likes, views, and a DataFrame of all comments
def nav_small_page(link):
    init_page(link)
    title = driver.find_element(By.CLASS_NAME,'title_text').text
    author = driver.find_element(By.CLASS_NAME,'nick_box').text
    post_datetime = datetime.strptime(driver.find_element(By.CLASS_NAME,'date').text, '%Y.%m.%d. %H:%M')
    text = '\n'.join([cont.text for cont in driver.find_elements(By.CLASS_NAME,'se-text-paragraph')])
    imgs = [img.get_attribute('src') for img in driver.find_elements(By.CLASS_NAME,'se-image-resource')]
    comment_elems = driver.find_elements(By.CLASS_NAME,'CommentItem')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        results = executor.map(gather_comment_info, comment_elems)
    all_comments = [result for result in results if result is not None]
    likes = driver.find_element(By.CLASS_NAME,'u_cnt').text
    views = driver.find_element(By.CLASS_NAME,'count').text[3:]
    comment_df = make_comment(all_comments)
    return title,author,post_datetime,text,imgs,likes,views,comment_df

# Iterate through each page of the base url and save results to a CSV file
def nav_big_page(base):
    page = 1
    print(base[0])
    # init_directory(base[0])
    res = pd.DataFrame(columns = ['Post ID','Href','Title','Author','Timestamp','Text','Images','Likes','Views','Comment Author','Comment Timestamp','Comment Text'])
    while page < (base[2]+1):
        try:
            print(f'Page {page}...',end='')
            sys.stdout.flush()
            count = 1
            init_page(base[1]+str(page))
            num_links = gather_links()
        except Exception as e:
            print('Failed on page',page)
            print('URL:',link)
            print(e)
            sys.stdout.flush()
        else:
            for num,link in num_links[:]:
                # try:
                title,author,post_datetime,text,imgs,likes,views,comment_df = nav_small_page(link)
                df = pd.DataFrame(np.array([num,link,title,author,post_datetime,text,imgs,likes,views],dtype=object).reshape(1,-1),columns=['Post ID','Href','Title','Author','Timestamp','Text','Images','Likes','Views'])
                pc = pd.concat([df,comment_df],axis=1)
                res = pd.concat([res,pc])
                print('.',end='')
                count += 1
                sys.stdout.flush()
        print()
        page += 1
    res.to_csv(f'teamsis_{base[0]}.csv',encoding='utf-8-sig',index=False,escapechar='\\')
    

def main():
    login('iafent','fkvpsxm1!')
    for b in base_urls:
        nav_big_page(b)
    driver.quit()

if __name__ == '__main__':
    main()