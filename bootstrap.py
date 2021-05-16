#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup as Bs4
import json
import re
import warnings

warnings.filterwarnings("ignore")  # suppress ssl cert warnings

'''
Todo
add md5 hash check? scrape md5 hash...
add README.md and fix requirements.txt
remove all whitespace from commands
re.sub does not work with raw string format?
'''

'''
JSON scheme
{
'Package Name': {                                         ---string
        'Version': '1.0.0',                               ---string
        'URL': ['http://asdfasdfasdf','http://.patch],    ---array (includes patches urls)
        'Deps': {                                         ---dict 
            'Required': ['first', 'second'],              ---array 
            'Recommended': ['first', 'second'],           ---array 
            'Optional': ['first', 'second']               ---array 
            }, 
        'Commands': ['Installation commands']             ---array
        }
}
'''

baseUrl = 'https://www.linuxfromscratch.org/blfs/view/stable/longindex.html'  # URL containing all package urls

links = []
scheme = {}
PkgCount = 0


def StripText(string):
    return re.sub(r'\n\s+', ' ', string)


def packageCollect(package, tagClass, tag):
    name = StripText(package.find(tag, class_=tagClass).text).strip()  # string of name

    deps = {'required': [], 'recommended': [], 'optional': []}
    for c in deps:
        for d in package.find_all('p', class_=c):
            for e in d.find_all('a', title=True, class_='xref'):  # grab blfs deps
                deps[c].append(StripText(e['title']))

            for e in d.find_all('a', class_='ulink'):  # grab external deps
                deps[c].append(StripText(e.text))
                scheme[StripText(e.text)] = {'name': name, 'url': [e['href']], "Dependencies": {
                    "required": [],
                    "recommended": [],
                    "optional": []
                }, 'Commands': []}  # manually add url to scheme
        # improve above code to save space?

    commands = []
    for d in package.find_all('kbd', class_='command'):  # remove whitespace
        commands.append(re.sub("\s+", " ", re.sub("\s+\\\\\\n\s+", ' ', d.text).replace('\n', ' ')))

    urls = []
    if package.find('div', class_='itemizedlist'):
        for d in package.find_all('div', class_='itemizedlist'):
            for e in d.find_all('a', class_='ulink'):  # if package has urls add to array
                urls.append(e['href'])

    print("Downloading info for {0}".format(name))
    scheme[name] = {'name': name, 'url': urls, 'Dependencies': deps, 'Commands': commands}


res = requests.get(baseUrl, verify=False)  # Begin...
soup = Bs4(res.text, 'html.parser')
el = soup.find('a', attrs={"id": "package-index"}).parent.next_sibling.next_sibling
print("Collecting base URLs....")
for i in el.find_all('a', href=True):  # for every url... check if has hashtag... if not add to array
    if not '#' in i['href']:
        links.append('https://www.linuxfromscratch.org/blfs/view/stable/' + i['href'])


for a in links:
    PkgCount += 1
    res = requests.get(a.rstrip(), verify=False)
    soup = Bs4(res.text, 'html.parser')  # get webpage contents

    if len(soup.find_all('div', class_='sect2')) > 1:  # if soup is module instead of std package
        for module in soup.find_all('div', class_='sect2'):
            if module.find_all('div', class_='package'):  # limit to modules only
                packageCollect(module, "sect2", "h2")  # call function on module
    else:
        packageCollect(soup, "sect1", "h1")  # call function on std package

if PkgCount == len(links):
    print('All packages successfully downloaded!')
else:
    print('Not all packages have been downloaded...')
    print('Number of urls: {}'.format(str(len(links))))
    print('Number of downloaded packages: {}'.format(PkgCount))

with open('dependencies.json', 'w+') as b:  # dump info to json file
    json.dump(scheme, b)
