from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import random as r
import csv
import sys


base_url = "https://daedamo.com/job?overlaps=5&page="
opp = Options()
# opp.add_experimental_option('excludeSwitches', ['enable-logging'])
# opp.add_argument('--no-sandbox')
# opp.add_argument('--disabled-dev-shm-usage')
opp.add_argument('--blink-settings=imagesEnabled=false')
driver = webdriver.Chrome(options=opp)  # You can use other drivers as well (e.g., Firefox)


def login(user,pw):
    driver.get('https://daedamo.com/new/bbs/login.php')
    driver.implicitly_wait(1.5 + (0.1 * r.randint(5,10)))
    driver.find_element('id','login_id').send_keys(user)
    driver.find_element('id','login_pw').send_keys(pw)
    driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div[2]/form/div[2]/div[2]/input').click()
    WebDriverWait(driver,60).until_not(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div[2]/div/div[2]/form/div[2]/div[2]/input')))

def init_page(url):
    print(url)
    driver.get(url)
    driver.implicitly_wait(2 + (0.1 * r.randint(5,10)))

def gather_links():
    print('here')
    articles = driver.find_elements(By.CLASS_NAME,'list_wrap')
    links = []
    for article in articles:
        print('there')
        try:
            driver.find_element(By.CLASS_NAME,'i_lock_gray_16')
        except:
            links.append(article.find_element(By.CLASS_NAME,'mw_basic_list_subject').find_elements(By.TAG_NAME,'a')[1].get_attribute('href'))
    return links

def save_to_csv(lst):
    keys = ['Title','Author','Post Date','Text','Images','Views']
    try:
        with open('eval.csv','a',encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writerows(lst)
    except Exception as e:
        print('Unable to save CSV')
        print(e)

def nav_small_page(link,r_lst):
    init_page(link)
    try:
        author = driver.find_element(By.CLASS_NAME,'noneanonymousnick').find_element(By.CLASS_NAME,'sv_member').text
    except:
        author = driver.find_element(By.CLASS_NAME,'noneanonymousnick').find_element(By.CLASS_NAME,'sv_guest').text
    text = driver.find_element(By.CLASS_NAME,'mw_basic_view_content').find_element(By.TAG_NAME,'div').find_element(By.ID,'view_content').text
    for restricted in r_lst:
        text = text.replace(restricted,'')
    title = driver.find_element(By.TAG_NAME,'h1').text
    try:
        driver.find_element(By.CLASS_NAME,'i_reply_gray_16')
    except:
        if title[0:5] == '[re] ':
            title = title[5:]
        r_lst.append(author)
    else:
        r_lst = []
    post_datetime = driver.find_element(By.TAG_NAME,'time').get_attribute('datetime')
    imgs = [img.get_attribute('src') for img in driver.find_elements(By.CLASS_NAME,'lazy.content-image')]
    views = driver.find_element(By.CLASS_NAME,'hit').text
    return title,author,post_datetime,text,imgs,views,r_lst

def nav_big_page():
    for page in range(1,11):
        try:
            init_page(base_url+str(page))
            count = 1
            links = gather_links()
        except Exception as e:
            print('Failed on page',page)
            print(e)
            sys.stdout.flush()
        else:
            lst = []
            r_lst = []
            for link in links:
                try:
                    title,author,post_datetime,text,imgs,views,re_lst = nav_small_page(link,r_lst)
                    r_lst = re_lst
                    lst.append({
                            'Title':title,
                            'Author':author,
                            'Post Date':post_datetime,
                            'Text':text,
                            'Images':imgs,
                            'Views':views
                        })
                except Exception as e:
                    print('Failed to complete post',count)
                    print(link)
                    print(e)
                    sys.stdout.flush()
                    continue
            count += 1
            save_to_csv(lst)
            
        
        print()
        page += 1

def init_directory():
    keys = ['Title','Author','Post Date','Text','Images','Views']
    with open('eval.csv','w',encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()

def main():
    init_directory()
    login('dataflow28','flowdata2833!!')
    nav_big_page()
    driver.close()

if __name__ == '__main__':
    main()
