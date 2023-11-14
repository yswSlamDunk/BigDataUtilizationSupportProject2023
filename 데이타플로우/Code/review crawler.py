from requests_html import HTMLSession
import csv
import sys

s = HTMLSession()
baseurl = 'https://daedamo.com/consulting?overlaps=4&page='

def get_response(page):
    url = baseurl+str(page)
    return s.get(url)

def parse_info(hosp,rating,tags,conts):
    rat,pharm,pres,price,loc = 'n/a','n/a','n/a','n/a','n/a'
    if rating:
        rat = rating.text.strip()
    for tag,cont in zip(tags,conts):
        if tag.text.strip() == '약국이름':
            pharm = cont.text.strip()
        elif tag.text.strip() == '처방정보':
            pres = cont.text.strip()
        elif tag.text.strip() == '처방금액':
            price = cont.text.strip()
        elif tag.text.strip() == '약국위치':
            loc = cont.text.strip()
        else:
            print('unknown tag')
    info = {
        'Hospital': hosp,
        'Rating': rat,
        'Pharmacy': pharm,
        'Prescription': pres,
        'Price': price,
        'Location': loc
    }
    return info

def save_csv(info):
    keys = ['Hospital','Rating','Pharmacy','Prescription','Price','Location']
    with open('reviews.csv','w',encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()
        dict_writer.writerows(info)

def nav_pages():
    page = 1
    r = get_response(page)
    if r.status_code != 200:
        print("URL Status Code:",r.status_code)
        return
    all_info = []
    print('Working...',end='')
    sys.stdout.flush()
    while (r.html.find('div#consult_wrap',first=True).text):
        hospitals = r.html.find('div.consult_div')
        for h in hospitals:
            name = h.find('div.hos_name',first=True).text.strip()
            rating = h.find('div.star_score',first=True)
            tags = h.find('div.tag')
            conts = h.find('div.cont')
            info = parse_info(name,rating,tags,conts)
            all_info.append(info)
        if page % 2 == 0:
            print('.',end='')
            sys.stdout.flush()
        page += 1
        r = get_response(page)
        
    return all_info

def main():
    info = nav_pages()
    save_csv(info)
    
if __name__ == '__main__':
    main()


