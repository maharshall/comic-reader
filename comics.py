# Alexander Marshall

import os
import cv2 
import json
import requests 
import webbrowser 
import urllib.request
from fpdf import FPDF
from bs4 import BeautifulSoup
from fuzzywuzzy import process
from prettytable import PrettyTable

# clears the terminal screen
def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

# generates a soup object from the given url
def get_soup(url):
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    return BeautifulSoup(page.content, 'html.parser')

# updates an item in the readlist
def update_item(key, title, url, read, total, status):
    data = get_readlist()
    data.update({key: {'title':title, 'url':url, 'read':read, 'total':total, 'status':status}})
    write_readlist(data)

# generates a dictionary from the json file
def get_readlist():
    if os.path.getsize('readlist.json') > 0:
        data = json.load(open('readlist.json', 'r'))
        return data
    return {}

# writes dictionary to json file
def write_readlist(data):
    json.dump(data, open('readlist.json', 'w'))

# prompts the user to search for a comic and make a selection
def add_to_readlist(query, p=1):
    query = query.replace(' ', '+')
    soup = get_soup('https://www.comicextra.com/comic-search?key='+query+'&page='+str(p))

    results = soup.find_all('div', class_='cartoon-box')
    table = PrettyTable(['#', 'Name', 'Issues', 'Released', 'Status'])
    table.align = 'l'

    for i in range(len(results)):
        details = results[i].find_all('div', class_='detail')
        status = details[1].text[8:]
        released = details[2].text[10:]
        total = get_total_issues(results[i].a['href'])
        table.add_row([i, results[i].h3.text, total, released, status])

    print('Page: '+str(p))
    print(table)

    print('\n[n] Next Page  [b] Go Back  [q] Quit')

    sel = input("\nSelection: ")

    if sel == 'n':
        add_to_readlist(query, p+1)
        clear()
    elif sel == 'b':
        main()
    elif sel == 'q':
        exit()
    elif sel.isdigit():
        confirm = input("add {} to readlist? (y/n): ".format(results[int(sel)].h3.text))
        if confirm == 'y':
            data = get_readlist()

            row = table[int(sel)]
            row.border = False
            row.header = False
            title = row.get_string(fields=['Name']).strip()

            if title in data.keys():
                print('Comic is already in readlist')
                main()

            url = results[int(sel)].a['href']
            total = get_total_issues(url)
            status = results[int(sel)].find_all('div', class_='detail')[1].text[8:]

            update_item(title, results[int(sel)].h3.text, results[int(sel)].a['href'], 0, total, status)
    main()

# prints the readlist to the terminal in a nice looking table
def print_readlist():
    data = get_readlist()
    table = PrettyTable(['#', 'Name', 'Issues Read', 'Status'])
    table.align = 'l'
    i = 0
    for key in sorted(data.keys()):
        table.add_row([i, data[key]['title'], str(data[key]['read'])+'/'+str(data[key]['total']), data[key]['status']])
        i += 1
    print(table)
    print('\n[a] Add to List  [u] Update  [b] Go Back  [q] Quit')
    selection = input('\nSelection: ')
    clear()

    if len(selection) > 3:
        # attempt fuzzy match
        comic_detail_view(process.extractOne(selection, data.keys())[0])
    elif selection == 'a':
        query = input("Enter Search: ")
        clear()
        add_to_readlist(query, 1)
    elif selection == 'u':
        update_readlist()
        print_readlist()
    elif selection == 'b':
        main()
    elif selection == 'q':
        exit()
    elif selection.isdigit():
        row = table[int(selection)]
        row.border = False
        row.header = False
        comic_detail_view(row.get_string(fields=['Name']).strip())
    else:
        main()

# get the total available issues for the comic at the given url
def get_total_issues(url):
    soup = get_soup(url)

    issues = soup.find_all('tr')
    return len(issues)

# prints the details of a single comic
def comic_detail_view(selection):
    data = get_readlist()
    comic = data[selection]

    table = PrettyTable(['Name', 'Issues Read', 'Status'])
    table.align = 'l'
    table.add_row([comic['title'], str(comic['read'])+'/'+str(comic['total']), comic['status']])
    print(table)
    print('[r] Read  [e] Edit Issues Read  [u] Update  [d] Delete from List  [b] Go Back  [q] Quit')
    sel = input('\nSelection: ')

    if sel == 'r':
        read_comic(selection)
    elif sel == 'e':
        issues = input('How many issues have you read? ')
        if int(issues) > comic['total']:
            print('That doesn\'t seem right...')
            clear()
            comic_detail_view(selection)
        clear()
        update_item(selection, comic['title'], comic['url'], int(issues), comic['total'], comic['status'])
        comic_detail_view(selection)
    elif sel == 'u':
        update_comic(selection)
        comic_detail_view(selection)
    elif sel == 'd':
        confirm = input('Are you sure you want to remove {} from readlist? (y/n): '.format(comic['title']))
        clear()
        if confirm == 'y':
            del data[selection]
            write_readlist(data)
            print_readlist()
        else:
            comic_detail_view(selection)
    elif sel == 'b':
        main()
    elif sel == 'q':
        exit()
    else:
        main()

# gets the next issue of the selected comic, downloads images, combines them to pdf, and removes images
def read_comic(selection):
    data = get_readlist()
    comic = data[selection]

    if comic['read'] == comic['total']:
        print('There are no more issues to read for this comic!')
        main()

    soup = get_soup(comic['url'])

    issues = soup.find_all("tr")[comic['total']-comic['read']-1]
    print('Loading '+issues.find("td").a.text+'...')
    url = issues.find("td").a['href']+'/full'

    soup = get_soup(url)
    pages = soup.find_all('img', class_='chapter_img')

    if not os.path.exists('images'):
        os.mkdir('images')
    
    pdf = FPDF()
    pdf.set_auto_page_break(0)

    for i in range(len(pages)):
        urllib.request.urlretrieve(pages[i]['src'], "images/"+str(i)+".jpg")

    # for i in range(len(os.listdir('images'))):
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
    update_item(selection, comic['title'], comic['url'], comic['read']+1, comic['total'], comic['status'])
    webbrowser.open(r'comic.pdf')
    clear()
    comic_detail_view(selection)

# checks all the comics in the readlist for new issues and changes in status
def update_readlist():
    print('Updating comcis...')
    data = get_readlist()
    if data is None:
        return None
    for key in data:
        comic = data[key]
        soup = get_soup(comic['url'])

        total = get_total_issues(comic['url'])
        status = soup.find_all('dd')[1].a.text

        if total > comic['total']:
            print('New issue of '+key)

        update_item(key, comic['title'], comic['url'], comic['read'], total, status)
    clear()

# checks a single comic for new issues and changes in status
def update_comic(key):
    print('Updating comic...')
    data = get_readlist()
    comic = data[key]
    soup = get_soup(comic['url'])

    total = get_total_issues(comic['url'])
    status = soup.find_all('dd')[1].a.text

    if total > comic['total']:
        print('New issue of '+key)

    update_item(key, comic['title'], comic['url'], comic['read'], total, status)
    clear()
        
def main():
    clear()
    print_readlist()

if __name__ == "__main__":
    main()
