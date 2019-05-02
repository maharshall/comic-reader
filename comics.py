# Alexander Marshall

import cv2
import numpy
import glob
import os
import requests
from bs4 import BeautifulSoup
import pprint
import urllib.request
from fpdf import FPDF
import webbrowser

query = input("Enter search: ")
query = query.replace(' ', '+')
url = 'https://www.comicextra.com/comic-search?key='+query
page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find_all('div', class_='cartoon-box')

for i in range(len(results)):
    print("[{}] {}".format(i, results[i].h3.text))

sel = input("select a comic: ")
url = results[int(sel)].a['href']

page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
soup = BeautifulSoup(page.content, 'html.parser')

issues = soup.find_all("tr")

for i in range(len(issues)):
    td = issues[i].find_all("td")
    link = td[0]
    date = td[1]
    print('[{}] {} {}'.format(i, date.text.strip('\n'), link.text.strip('\n')))

sel = input("select an issue to read: ")
url = issues[i].find("td").a['href']+'/full'

page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
soup = BeautifulSoup(page.content, 'html.parser')

pages = soup.find_all('img', class_='chapter_img')

print('Getting images... ', end='')
for i in range(len(pages)):
    urllib.request.urlretrieve(pages[i]['src'], "images/"+str(i)+".jpg")
print('Done')

pdf = FPDF()
pdf.set_auto_page_break(0)

print('Combining images to pdf... ', end='')
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
print('Done')
webbrowser.open(r'comic.pdf')