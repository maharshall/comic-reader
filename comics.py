# Alexander Marshall

import cv2
import os
import requests
from bs4 import BeautifulSoup
import pprint
import urllib.request
from fpdf import FPDF
import webbrowser
import json

def add_to_readlist():
    query = input("Enter search: ")
    query = query.replace(' ', '+')
    url = 'https://www.comicextra.com/comic-search?key='+query
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find_all('div', class_='cartoon-box')

    for i in range(len(results)):
        print("[{}] {}".format(i, results[i].h3.text))

    sel = input("select a comic: ")
    confirm = input("add {} to readlist? (y/n): ".format(results[int(sel)].h3.text))
    if confirm == 'y':
        url = results[int(sel)].a['href']
        data = get_readlist()
        if data == None:
            data = {}

        data.update({results[int(sel)].h3.text: {'title':results[int(sel)].h3.text,
            'url':results[int(sel)].a['href'],
            'read':0}})
        write_readlist(data)    

def get_readlist():
    if os.path.getsize('readlist.json') > 0:# Alexander Marshall

import cv2
import os
import requests
from bs4 import BeautifulSoup
import pprint
import urllib.request
from fpdf import FPDF
import webbrowser
import json

def add_to_readlist():
    query = input("Enter search: ")
    query = query.replace(' ', '+')
    url = 'https://www.comicextra.com/comic-search?key='+query
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find_all('div', class_='cartoon-box')

    for i in range(len(results)):
        details = results[i].find_all('div', class_='detail')
        print("\n[{}] {}".format(i, results[i].h3.text))
        for detail in details:
            print(' '+detail.text.replace('\n', ''))

    sel = input("select a comic: ")
    confirm = input("add {} to readlist? (y/n): ".format(results[int(sel)].h3.text))
    if confirm == 'y':
        url = results[int(sel)].a['href']
        data = get_readlist()
        total = get_total_issues(url)
        status = results[int(sel)].find_all('div', class_='detail')[1].text[8:]
        
        if data == None:
            data = {}

        data.update({len(data): {'title':results[int(sel)].h3.text,
            'url':results[int(sel)].a['href'],
            'read':0,
            'total':total,
            'status':status}})
        
        write_readlist(data)    
    main()

def get_readlist():
    if os.path.getsize('readlist.json') > 0:
        data = json.load(open('readlist.json', 'r'))
        return data
    else:
        return None

def write_readlist(data):
    json.dump(data, open('readlist.json', 'w'))

def print_readlist():
    data = json.load(open('readlist.json', 'r'))
    i = 0
    for key in data:
        print('[{}] {} \t{}/{} ({})'.format(key, data[key]['title'], data[key]['read'], data[key]['total'], data[key]['status']))
        i += 1
    print('\n[{}] Go Back'.format(i))
    print('[{}] Quit'.format(i+1))

def get_total_issues(url):
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    issues = soup.find_all('tr')
    return len(issues)


def read_comic(selection):
    data = get_readlist()

    if int(selection) == len(data):
        main()
    if int(selection) > len(data):
        exit()

    comic = data[selection]

    if comic['read'] == comic['total']:
        print('There are no more issues to read for this comic')
        main()

    url = comic['url']
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    issues = soup.find_all("tr")[comic['total']-comic['read']-1]
    url = issues.find("td").a['href']+'/full'

    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    pages = soup.find_all('img', class_='chapter_img')

    for i in range(len(pages)):
        urllib.request.urlretrieve(pages[i]['src'], "images/"+str(i)+".jpg")

    data.update({selection: {'title':comic['title'],
            'url':comic['url'],
            'read':comic['read']+1,
            'total':comic['total'],
            'status':comic['status']}})
    write_readlist(data) 
    combine_images()

def combine_images():
    pdf = FPDF()
    pdf.set_auto_page_break(0)

    for i in range (len(os.listdir('images'))):
        image = 'images/'+str(i)+'.jpg'
        img = cv2.imread(image)
        
        if img.shape[0] < img.shape[1]:
            pdf.add_page(orientation='L')
            pdf.image(image, x=0, y=0, h=210, w=297)
        else:
            pdf.add_page(orientation='P')
            pdf.image(image, x=0, y=0, w=210, h=297)

        os.remove(image)

    pdf.output('comic.pdf', 'F')
    webbrowser.open(r'comic.pdf')
    main()

def update_readlist():
    data = get_readlist()
    for key in data:
        comic = data[key]
        page = requests.get(comic['url'], headers={'User-Agent':'Mozilla/5.0'})
        soup = BeautifulSoup(page.content, 'html.parser')

        total = get_total_issues(comic['url'])
        status = soup.find_all('dd')[1].a.text

        data.update({key: {'title':comic['title'],
            'url':comic['url'],
            'read':comic['read'],
            'total':total,
            'status':status}})
    write_readlist(data) 
        

def main():
    update_readlist()
    sel = input('What would you like to do?\n[0] Add to List\n[1] Read from List\n[2] Quit\n\nSelection: ')
    if sel == '0':
        add_to_readlist()
    if sel == '1':
        print_readlist()
        selection = input('\nSelection: ')
        read_comic(selection)
    if sel == '2':
        exit()

if __name__== "__main__":
    main()
        data = json.load(open('readlist.json', 'r'))
        return data
    else:
        return None

def write_readlist(data):
    json.dump(data, open('readlist.json', 'w'))

def print_readlist():
    print('\n')
    data = json.load(open('readlist.json', 'r'))
    i = 0
    for key in data:
        print('[{}] {}'.format(i, key))
        i += 1


def read_comic(selection):
    data = get_readlist()
    comic = data[selection]
    url = 'https://comicextra.com/'+comic['title'].lower().replace(' ', '-')+'/'+'chapter-'+str(comic['read']+1)+'/full'.replace('/comic', '')
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')


    # issues = soup.find_all("tr")

    # for i in range(len(issues)):
    #     td = issues[i].find_all("td")
    #     link = td[0]
    #     date = td[1]
    #     print('[{}] {} {}'.format(i, date.text.strip('\n'), link.text.strip('\n')))

    # sel = input("select an issue to read: ")
    # url = issues[i].find("td").a['href']+'/full'

    # page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    # soup = BeautifulSoup(page.content, 'html.parser')

    pages = soup.find_all('img', class_='chapter_img')

    for i in range(len(pages)):
        urllib.request.urlretrieve(pages[i]['src'], "images/"+str(i)+".jpg")
    combine_images()


def combine_images():
    pdf = FPDF()
    pdf.set_auto_page_break(0)

    for i in range (len(os.listdir('images'))):
        image = 'images/'+str(i)+'.jpg'
        img = cv2.imread(image)
        
        if img.shape[0] < img.shape[1]:
            pdf.add_page(orientation='L')
            pdf.image(image, x=0, y=0, h=210, w=297)
        else:
            pdf.add_page(orientation='P')
            pdf.image(image, x=0, y=0, w=210, h=297)

        os.remove(image)

    pdf.output('comic.pdf', 'F')
    webbrowser.open(r'comic.pdf')


sel = input('What would you like to do?\n[0] add to list\n[1] read from list\n\nSelection: ')
if sel == '0':
    add_to_readlist()
if sel == '1':
    print_readlist()