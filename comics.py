# Alexander Marshall

import cv2, os, json, requests, webbrowser, urllib.request
from fpdf import FPDF
from bs4 import BeautifulSoup
from prettytable import PrettyTable

def clear():
    if os.name == 'nt': 
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def add_to_readlist(query, p=1):
    query = query.replace(' ', '+')
    url = 'https://www.comicextra.com/comic-search?key='+query+'&page='+str(p)
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

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
    if sel == 'b':
        main()
    if sel == 'q':
        exit()

    confirm = input("add {} to readlist? (y/n): ".format(results[int(sel)].h3.text))
    if confirm == 'y':
        data = get_readlist()

        row = table[int(sel)]
        row.border = False
        row.header = False

        if row.get_string(fields=['Name']).strip() in data.keys():
            print('Comic is already in readlist')
            main()

        url = results[int(sel)].a['href']
        total = get_total_issues(url)
        status = results[int(sel)].find_all('div', class_='detail')[1].text[8:]

        data.update({row.get_string(fields=['Name']).strip(): {'title':results[int(sel)].h3.text,
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
    return {}

def write_readlist(data):
    json.dump(data, open('readlist.json', 'w'))

def print_readlist():
    data = json.load(open('readlist.json', 'r'))
    table = PrettyTable(['#', 'Name', 'Issues Read', 'Status'])
    table.align = 'l'
    for key in data:
        table.add_row([i, data[key]['title'], str(data[key]['read'])+'/'+str(data[key]['total']), data[key]['status']])
    print(table)
    print('\n[a] Add to List  [b] Go Back  [q] Quit')
    selection = input('\nSelection: ')
    clear()

    if selection == 'a':
        query = input("Enter Search: ")
        clear()
        add_to_readlist(query, 1)
    if selection == 'b':
        main()
    if selection == 'q':
        exit()

    row = table[int(selection)]
    row.border = False
    row.header = False
    comic_detail_view(row.get_string(fields=['Name']).strip())

def get_total_issues(url):
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    issues = soup.find_all('tr')
    return len(issues)

def comic_detail_view(selection):
    data = get_readlist()

    if selection == 'b':
        main()
    if selection == 'q':
        exit()

    table = PrettyTable(['Name', 'Issues Read', 'Status'])
    table.align = 'l'
    table.add_row([data[selection]['title'], str(data[selection]['read'])+'/'+str(data[selection]['total']), data[selection]['status']])
    print(table)
    print('[r] Read  [e] Edit Issues Read  [d] Delete from List  [b] Go Back  [q] Quit')
    sel = input('\nSelection: ')

    if sel == 'r':
        read_comic(selection)
    if sel == 'e':
        issues = input('How many issues have you read? ')
        if int(issues) > data[selection]['total']:
            print('That doesn\'t seem right...')
            clear()
            comic_detail_view(selection)
        clear()
        data.update({selection: {'title':data[selection]['title'],
            'url':data[selection]['url'],
            'read':int(issues),
            'total':data[selection]['total'],
            'status':data[selection]['status']}})
        write_readlist(data)
        comic_detail_view(selection)
    if sel == 'd':
        confirm = input('Are you sure you want to remove {} from readlist? (y/n)'.format(data[selection]['title']))
        clear()
        if confirm == 'y':
            del data[selection]
            write_readlist(data)
            print_readlist()
        else:
            comic_detail_view(selection)
    if sel == 'b':
        main()
    if sel == 'q':
        exit()

def read_comic(selection):
    data = get_readlist()

    comic = data[selection]

    if comic['read'] == comic['total']:
        print('There are no more issues to read for this comic!')
        main()

    url = comic['url']
    page = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    issues = soup.find_all("tr")[comic['total']-comic['read']-1]
    print('Loading '+issues.find("td").a.text+'...')
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

    pdf = FPDF()
    pdf.set_auto_page_break(0)

    for i in range(len(os.listdir('images'))):
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
    clear()
    print('[n] Read Next Issue [b] Go Back [q] Quit')
    sel = input('\nSelection: ')
    clear()

    if sel == 'n':
        read_comic(selection)
    if sel == 'b':
        main()
    if sel == 'q':
        exit()

def update_readlist():
    data = get_readlist()
    if data is None:
        return None
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
    clear()
    print_readlist()

if __name__ == "__main__":
    print('Updating comcis...')
    update_readlist()
    main()
