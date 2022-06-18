import os
import time
import requests
from bs4 import BeautifulSoup
import sys

start = time.time()
url = "http://mpsi2llg.free.fr/mpsi2-physique.html"
html = requests.get(url).content
soup = BeautifulSoup(html, "lxml")
path = os.getcwd()
open('404.txt', 'w').close()


def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c, '')
    if value[-1] == ' ':
        value = value[:-1]
    if value[0] == ' ':
        value = value[1:]
    return value


def parse(text):
    L = []
    for i in range(4, len(text)):
        if text[i] == '-':
            L.append('')
        else:
            L[-1] += text[i]
    return L


def writeTo404(str):
    absent = open('404.txt', 'a')
    absent.write(str + '\n')
    absent.close()


# with download=False, you don't get the 404 list.
def scrape(soup, download):

    links = soup.find_all('a', href=True)

    for l in links:
        link = l.get('href')
        # if link.endswith('.pdf') or link.endswith('.py') or link.endswith('.ipynb'):
        if not link.startswith('http:') and not link.startswith("https:") and not link.startswith("#"):
            if link.startswith('pdf'):
                link = "http://mpsi2llg.free.fr/" + link

            if link.startswith("file:"):
                writeTo404(link)
                continue
            if download:
                response = requests.get(link)
                if response.status_code == 404:
                    writeTo404(link)
                    continue

            # print('Found a file:', link)
            folder = l
            error = False
            name = ""
            outline = False

            try:
                while folder.get('id') is None or not folder.get('id').startswith('text-'):
                    try:
                        cl = folder.get('class')[0]
                        if cl.startswith('outline-'): # and not cl.startswith('outline-text-'):
                            outline = True
                            break
                    except TypeError:
                        pass
                    folder = folder.parent
            except:
                sys.stderr.write("Skipped pdf, cause: toRoot: " + link + '\n')
                error = True
                continue
            if not outline:
                L = parse(folder.get('id'))
                if len(L) == 4:
                    name = L[-1] + ' - ' + folder.parent.a.next_sibling.text
                elif len(L) == 2:
                    name = L[-1] + ' - ' + folder.parent.h3.find_next(text=True)
                elif len(L) == 3:
                    name = L[-1] + ' - ' + folder.parent.h4.find_next(text=True).find_next(text=True)
                else:
                    name = L[-1] + ' - ' + folder.parent.h2.find_next(text=True).find_next(text=True)
                name = remove(name, '\\/:*?"<>|')

                folder = folder.parent
            while folder.get('class') != 'outline-2':
                try:
                    while folder.get('class') is None or not folder.get('class')[0].startswith('outline-'):
                        folder = folder.parent
                except Exception as e:
                    print(e)
                    # sys.stderr.write("Skipped pdf, cause: toRoot: " + link + '\n')
                    # error = True
                    break
                nb = folder.get('class')[0][-1]
                name_folder = parse(folder.div.get('id'))[-1] + ' -' + folder.find('h'+nb).find_next(text=True).find_next(text=True)
                name_folder = remove(name_folder, '\\/:*?"<>|')
                name = name_folder + '/' + name
                #print(name)
                if folder.get('class')[0] == 'outline-2':
                    break
                folder = folder.parent

            if download:
                try:
                    os.makedirs(path + '/' + name)
                except FileExistsError:
                    pass
                pdf = open(path + '/' + name + '/' + link[28:], 'wb')
                pdf.write(response.content)
                pdf.close()
                print("Downloaded:", link)

                if link.startswith("http://mpsi2llg.free.fr/pdf/"):
                    l['href'] = name + '/' + link[28:]
                elif link.startswith("http://mpsi2llg.free.fr/"):
                    l['href'] = name + '/' + link[24:]
                    print("You have to download", link)

            else:
                pass
                #time.sleep(0.)

            if error:
                sys.stderr.write("Error while processing file: " + link + '\n')
                continue

    if download:
        mainFile = open(path + '/mpsi2-physique.html', 'wb')
        mainFile.write(soup.prettify('utf-8'))
        mainFile.close()
        print("Saved new index file!\nDone in", time.time()-start, "secs")


scrape(soup, True)
