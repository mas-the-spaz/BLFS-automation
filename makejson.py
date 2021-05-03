import requests
from bs4 import BeautifulSoup as bs4
import json
import re


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


def getInfo(i):
        res = requests.get(i.rstrip(), verify=False)
        soup = bs4(res.text, 'html.parser')
        name = soup.find("h1", class_='sect1').find('a').get('id')  # string of name
        version = soup.find("h1", class_='sect1').text.strip()  # string of version
        deps = {'recommended': [], 'required': [], 'optional': []}
        # if div class=sect2... in content,
        # for each sect2 div, set all the vars etc. 

        def depDict(type):
            for i in soup.find_all('p', class_=type):
                for j in i.find_all('a', title=True, class_='xref'): # grab blfs deps
                   deps[type].append(j['title'])

                for j in i.find_all('a', class_='ulink'): # greb external deps
                    deps[type].append(j.text)
                    scheme[j.text] = {'url': j['href']}
                

        for i in ['required', ' recommended', 'optional']:
            depDict(i)

        commands = []
        for i in soup.find_all('kbd', class_='command'):  # remove whitespace
            commands.append(re.sub('\s+\\\\\s+', ' ', i.text).replace('\n', ' '))

        urls = []
        for i in soup.find('div', class_='itemizedlist').find_all('a', class_='ulink'):
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
            getInfo(i)



with open('dependencies.json', 'w+') as j:
    json.dump(scheme, j)


