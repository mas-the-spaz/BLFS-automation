from typing import TextIO

import requests
from bs4 import BeautifulSoup as bs4
import json
import re

baseUrl = 'https://github.com/mas-the-spaz/python-blfs.git'

scheme = {}

'''
JSON scheme
{
'Package Name': { 
        'Version': '1.0.0',                               ---string
        'URL': ['http://asdfasdfasdf','http://patch],     ---array (includes patches)
        'Deps': {                                         ---dict or None
            'Required': ['first', 'second'],              ---array or None
            'Recommended': ['first', 'second'],           ---array or None
            'Optional': ['first', 'second']               ---array or None
            }, 
        'Commands': ['Installation commands']             ---array
        }
}
'''

def packageCollect(package, tagClass, tag):
    version = package.find(tag, class_=tagClass).text.strip()  # string of version
    name = package.find(tag, class_=tagClass).find('a').get('id')  # string of name

    deps = {'required': [], 'recommended': [], 'optional': []}  # remove redundancy?
    for y in ['required', 'recommended', 'optional']:
        for i in package.find_all('p', class_=y):
            for j in i.find_all('a', title=True, class_='xref'):  # grab blfs deps
                deps[y].append(j['title'])

            for j in i.find_all('a', class_='ulink'):  # grab external deps
                deps[y].append(j.text)
                scheme[j.text.replace('\n', ' ')] = {'url': j['href']}  # get md5 ?

    commands = []
    for i in package.find_all('kbd', class_='command'):  # remove whitespace
        commands.append(re.sub('\s+\\\\\s+', ' ', i.text))

    urls = []
    if package.find('div', class_='itemizedlist'):
        for i in package.find('div', class_='itemizedlist').find_all('a', class_='ulink'):
            # if url starts with ftp... --- for dl script
            # check if returns something
            urls.append(i['href'])

    print("Downloading {0} with deps: {1} \n urls: {2}".format(name, str(deps), str(urls)))
    scheme[name] = {'Version': version, 'url': urls, 'Dependencies': deps, 'Commands': commands}


with open('Wishlist.txt', 'r+') as u:  # eventually this will download the original urls
    for i in u.readlines():
        if not '#' in i:  # remove all modules urls 
            res = requests.get(i.rstrip(), verify=False)
            soup = bs4(res.text, 'html.parser')  # get webpage contents

            if soup.find_all('div', class_='sect2'):  # if soup is module instead of std package
                for module in soup.find_all('div', class_='sect2'):
                    if module.find_all('div', class_='package'):  # limit to modules only
                        packageCollect(module, "sect2", "h2")
            else:
                packageCollect(soup, "sect1", "h1")

with open('dependencies.json', 'w+') as j:
    json.dump(scheme, j)


