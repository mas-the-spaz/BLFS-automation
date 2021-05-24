#!/usr/bin/python3

import requests
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

links = []
scheme = {}
PkgCount = 0


def StripText(string):
    return re.sub(r'\n\s+', ' ', string)


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
        # improve above code to save space?

    commands = []
    for d in package.find_all('kbd', class_='command'):  # remove whitespace
        if 'EOF' in d.text:  # fixes Heredoc bug
            commands.append(d.text)
        else:
            commands.append(re.sub("\s+", " ", re.sub("\s+\\\\\\n\s+", ' ', d.text).replace('\n', ' ')))

    kconf = []
    if package.find('div', class_='kernel'):
        for g in package.find_all('div', class_='kernel'):
            for h in g.find_all('pre', class_='screen'):
                kconf.extend(h.find('code', class_='literal'))


    urls = []
    hashes = []
    if package.find('div', class_='itemizedlist'):  # if package has urls add to array
        for d in package.find_all('div', class_='itemizedlist'):
            for e in d.find_all('a', class_='ulink'):  
                urls.append(e['href'])
            for f in d.find_all('p'):
                if 'Download MD5 sum:' in f.getText(): 
                    hashes.extend(f.getText().split()[-1:])
    
    print("Downloading info for {0}".format(name))
    scheme[name] = {'name': name, 'url': FtpUrlFilter(urls), 'Dependencies': deps, 'Commands': commands, 'Hashes': hashes, 'kconf': kconf}


res = requests.get(baseUrl, verify=False)  # Begin...
soup = Bs4(res.text, 'html.parser')
el = soup.find('a', attrs={"id": "package-index"}).parent.next_sibling.next_sibling
print("Collecting base URLs....")
for i in el.find_all('a', href=True):  # for every url... check if has href... if not add to array
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
