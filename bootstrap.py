#!/usr/bin/python3

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup as Bs4
import json
import re
import warnings

warnings.filterwarnings("ignore")  # suppress ssl cert warnings

'''
JSON scheme
{
'Package Name': {                                         ---string
        'Version': '1.0.0',                               ---string
        'URL': ['http://asdfasdfasdf','http://.patch],    ---list (includes patches urls)
        'Deps': {                                         ---dict 
            'Required': ['first', 'second'],              ---list 
            'Recommended': ['first', 'second'],           ---list 
            'Optional': ['first', 'second']               ---list 
            }, 
        'Commands': ['Installation commands'],            ---list
        'Hashes': ['9801095c42bba12edebd1902bcf0a990'],   ---list
        'Kconf': ['kernel configuration settings']        ---list
        }
}
'''

baseUrl = 'https://www.linuxfromscratch.org/blfs/view/stable/longindex.html'  # URL containing all package urls
# baseUrl = 'https://www.linuxfromscratch.org/blfs/view/stable-systemd/longindex.html' # uncomment this line if you are using the Systemd BLFS build.

scheme = {}
PkgCount = 0
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0'
}


def StripText(string):
    return re.sub(r'\n\s+', ' ', string)

def UrlGet(url):
    s = requests.Session()

    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])

    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))
    return s.get(url.rstrip(), verify=False, headers=headers, timeout=30)


def FtpUrlFilter(UrlsList):  # removes ftp links from url list, but only if they are duplicates
    NewList = []
    i = 0
    while i < len(UrlsList):
        if 'texlive' in UrlsList[i]:  # the texlive package only contains ftp urls
            return UrlsList
        if (i % 2) == 0:
            NewList.append(UrlsList[i])
        elif not 'ftp://' in UrlsList[i]:
            NewList.append(UrlsList[i])
        i += 1
    return NewList


def packageCollect(package, tagClass, tag):
    name = StripText(package.find(tag, class_=tagClass).text).strip()  # string of name

    deps = {'required': [], 'recommended': [], 'optional': []}
    for c in deps:
        for d in package.find_all('p', class_=c):
            for e in d.find_all('a', title=True, class_='xref'):  # grab blfs deps
                deps[c].append(StripText(e['title']))

            for e in d.find_all('a', class_='ulink'):  # grab external deps
                deps[c].append(StripText(e.text))
                scheme[StripText(e.text)] = {'name': StripText(e.text), 'url': [e['href']], "Dependencies": {
                    "required": [],
                    "recommended": [],
                    "optional": []
                }, 'Commands': []}  # manually add url to scheme


    commands = list(map(lambda d: d.text , package.find_all('kbd', class_='command')))

    kconf = list(map(lambda a: a.text, package.select('div.kernel pre.screen code.literal'))) 

    urls = []
    hashes = []
    u = list(map(lambda x: x['href'], package.select('div.itemizedlist a.ulink'))) 
    if package.find('div', class_='itemizedlist'):  # if package has urls add to array
        for d in package.find_all('div', class_='itemizedlist'):
            for e in d.find_all('a', class_='ulink'):  
                urls.append(e['href'])
            for f in d.find_all('p'):
                if 'Download MD5 sum:' in f.getText(): 
                    hashes.extend(f.getText().split()[-1:])
    
    print("Downloading info for {0}".format(name))
    scheme[name] = {'name': name, 'url': FtpUrlFilter(urls), 'Dependencies': deps, 'Commands': commands, 'Hashes': hashes, 'kconf': kconf}


res = UrlGet(baseUrl)  # Begin...
soup = Bs4(res.text, 'html.parser')
el = soup.find('a', attrs={"id": "package-index"}).parent.next_sibling.next_sibling
print("Collecting base URLs....")
# for every url... check if has href... if not add to array
links = list(map(lambda v: 'https://www.linuxfromscratch.org/blfs/view/stable/' + v['href'] if not '#' in v['href'] else None, el.find_all('a', href=True)))


for a in list(filter(None, links)):
    PkgCount += 1
    try:
        res = UrlGet(a)
    except requests.ConnectionError as e:
        print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
        print(str(e))  
        continue

    soup = Bs4(res.text, 'html.parser')  # get webpage contents

    if len(soup.find_all('div', class_='sect2')) > 1:  # if soup is module instead of std package
        for module in soup.find_all('div', class_='sect2'):
            if module.find_all('div', class_='package'):  # limit to modules only
                packageCollect(module, "sect2", "h2")  # call function on module
    else:
        packageCollect(soup, "sect1", "h1")  # call function on std package

if PkgCount == len(list(filter(None, links))):
    print('All packages successfully downloaded!')
else:
    print('Not all packages have been downloaded...')
    print('Number of urls: {}'.format(str(len(links))))
    print('Number of downloaded packages: {}'.format(PkgCount))

with open('dependencies.json', 'w+') as b:  # dump info to json file
    json.dump(scheme, b)
