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

BASEURL = 'https://www.linuxfromscratch.org/blfs/view/stable/longindex.html'  # URL containing all package urls
# BASEURL = 'https://www.linuxfromscratch.org/blfs/view/stable-systemd/longindex.html' # uncomment this line if you are using the Systemd BLFS build.

scheme = {}
pkg_count = 0
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0'
}


def strip_text(string):
    return re.sub(r'\n\s+', ' ', string)

def url_get(url):
    s = requests.Session()

    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])

    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))
    return s.get(url.rstrip(), verify=False, headers=headers, timeout=30)


def FTP_URL_filter(URL_list):  # removes ftp links from url list, but only if they are duplicates
    newlist = []
    i = 0
    while i < len(URL_list):
        if 'texlive' in URL_list[i]:  # the texlive package only contains ftp urls
            return URL_list
        if (i % 2) == 0:
            newlist.append(URL_list[i])
        elif not 'ftp://' in URL_list[i]:
            newlist.append(URL_list[i])
        i += 1
    return newlist


def package_collect(package, tag_class, tag):
    name = strip_text(package.find(tag, class_=tag_class).text).strip()  # string of name

    deps = {'required': [], 'recommended': [], 'optional': []}
    for c in deps:
        for d in package.find_all('p', class_=c):
            for e in d.find_all('a', title=True, class_='xref'):  # grab blfs deps
                deps[c].append(strip_text(e['title']))

            for e in d.find_all('a', class_='ulink'):  # grab external deps
                deps[c].append(strip_text(e.text))
                scheme[strip_text(e.text)] = {'name': strip_text(e.text), 'url': [e['href']], "Dependencies": {
                    "required": [],
                    "recommended": [],
                    "optional": []
                }, 'Commands': [], 'type': 'external'}  # manually add url to scheme


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
    scheme[name] = {'name': name, 'url': FTP_URL_filter(urls), 'Dependencies': deps, 'Commands': commands, 'Hashes': hashes, 'kconf': kconf, 'type': 'BLFS'}


res = url_get(BASEURL)  # Begin...
soup = Bs4(res.text, 'html.parser')
el = soup.find('a', attrs={"id": "package-index"}).parent.next_sibling.next_sibling
print("Collecting base URLs....")
# for every url... check if has href... if not add to array
links = list(map(lambda v: 'https://www.linuxfromscratch.org/blfs/view/stable/' + v['href'] if not '#' in v['href'] else None, el.find_all('a', href=True)))


for a in list(filter(None, links)):
    pkg_count += 1
    try:
        res = url_get(a)
    except requests.ConnectionError as e:
        print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
        print(str(e))  
        continue

    soup = Bs4(res.text, 'html.parser')  # get webpage contents

    if len(soup.find_all('div', class_='sect2')) > 1:  # if soup is module instead of std package
        for module in soup.find_all('div', class_='sect2'):
            if module.find_all('div', class_='package'):  # limit to modules only
                package_collect(module, "sect2", "h2")  # call function on module
    else:
        package_collect(soup, "sect1", "h1")  # call function on std package

if pkg_count == len(list(filter(None, links))):
    print('All packages successfully downloaded!')
else:
    print('Not all packages have been downloaded...')
    print('Number of urls: {}'.format(str(len(links))))
    print('Number of downloaded packages: {}'.format(pkg_count))

with open('dependencies.json', 'w+') as b:  # dump info to json file
    json.dump(scheme, b)
