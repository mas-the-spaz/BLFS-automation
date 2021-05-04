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
# create a class for handling web components?

def moduleCollect(soup):
    # if div sect2 than call this
    for module in soup.find_all('div', class_='sect2'):
        ### if conatins text 'package information'
        name = module.find('h2', class_='sect2').text.strip()
        urls = []
        for i in module.find('div', class_='itemizedlist').find_all('a', class_='ulink'):
            # if url starts with ftp... --- for dl script
            # check if returns something
            urls.append(i['href'])

        deps = {'recommended': [], 'required': [], 'optional': []}
        for y in ['required', 'recommended', 'optional']:   
            for i in module.find_all('p', class_=y):
                for j in i.find_all('a', title=True, class_='xref'): # grab blfs deps
                    deps[y].append(j['title'])

                for j in i.find_all('a', class_='ulink'): # greb external deps
                    deps[y].append(j.text)
                    scheme[j.text] = {'url': j['href']}
        
        commands = []
        for i in module.find_all('kbd', class_='command'):  # remove whitespace
            commands.append(re.sub('\s+\\\\\s+', ' ', i.text).replace('\n', ' '))

        print(name)
        print(deps)
        print(urls)
        print(commands)
        scheme[name] = {'Version': name, 'url': urls, 'Dependencies': deps, 'Commands': commands}

def packageCollect(package, tagClass, tag):
    version = package.find(tag, class_=tagClass).text.strip()  # string of version
    if package.find(tag, class_=tagClass).find('a').get('id'):
        name = package.find(tag, class_=tagClass).find('a').get('id')  # string of name
    else:
        name = version

    deps = {'recommended': [], 'required': [], 'optional': []}

    def depDict(type):
        for i in package.find_all('p', class_=type):
            for j in i.find_all('a', title=True, class_='xref'): # grab blfs deps
                deps[type].append(j['title'])

            for j in i.find_all('a', class_='ulink'): # greb external deps
                deps[type].append(j.text)
                scheme[j.text] = {'url': j['href']}  # get md5 ?

    for i in ['required', 'recommended', 'optional']:
        depDict(i)

    commands = []
    for i in package.find_all('kbd', class_='command'):  # remove whitespace
        commands.append(re.sub('\s+\\\\\s+', ' ', i.text).replace('\n', ' '))

    urls = []
    for i in package.find('div', class_='itemizedlist').find_all('a', class_='ulink'):
        # if url starts with ftp... --- for dl script
        # check if returns something
        urls.append(i['href'])

    print(urls)
    print(commands)
    print(name)
    print(version)
    print(deps)

    scheme[name] = {'Version': version, 'url': urls, 'Dependencies': deps, 'Commands': commands}



with open('Wishlist.txt', 'r+') as u:  # eventually this will download the orignal urls
    for i in u.readlines():
        if not '#' in i:  # remove all modules urls 
            res = requests.get(i.rstrip(), verify=False)
            soup = bs4(res.text, 'html.parser') # get webpage contents

            if soup.find_all('div', class_='sect2'):
                for module in soup.find_all('div', class_='sect2'):
                    packageCollect(module, "sect2", "h2")
                    # check if contains "packge information"
            else:
                packageCollect(soup, "sect1", "h1")
# consolidate into one function

with open('dependencies.json', 'w+') as j:
    json.dump(scheme, j)


