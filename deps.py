import argparse
import json
import os

errors = ["Dependencies.json not found! Try running bootstrap.py to rebuild dependency database",
          "no dependencies found for "]

extensions = ['.bz2', '.tar.xz', '.zip', '.tar.gz', '.patch', '.tgz']

'''
flags 
    list or DOWNLOAD?
    -l --list

    include recommended and optional?
    -r --recommended, -o --optional

    list commands (possibly output to shell) or NORMAL (download)
    -c --commands 

    package <name>  REQUIRED
    -p --package


main function
 
output specific order of installation 
check if ftp is only link - if yes download
check if package is already downloaded


'''

'''
JSON scheme
{
'Package Name': {                                         
        'Version': '1.0.0',                               
        'URL': ['http://asdfasdfasdf','http://patch],     
        'Deps': {                                         
            'Required': ['first', 'second'],              
            'Recommended': ['first', 'second'],           
            'Optional': ['first', 'second']               
            }, 
        'Commands': ['Installation commands']             
        }
}
'''

def FtpUrlCheck(UrlsList):
    # takes an array of urls (from the package dict) and performs check
    NewList = []
    # if index is odd (0, 2, etc) - add to new list
    # if index is even - if ftp:// is in [i] skip
    # else add to list 

    i = 0
    while i < len(UrlsList):
        if i % 2 == 0 and 'ftp://' in UrlsList[i]:
            NewList.append(UrlsList[i])
        i +=1
        print(NewList)
        


fff = ['ftp://sss', 'ftp://aaa', 'greg', 'ftp://hhh']


FtpUrlCheck(fff)


def ListCommands(dat, pkg):
    if not pkg in dat:
        print('{0} "{1}"'.format(errors[1], pkg))
        exit()
    for command in dat[pkg]['Commands']:  # list commands
        print(command)


def DownloadAll(dat, exts):  # list (eventually download) all packages
    for package in dat:
        for url in dat[package]['url']:
            for i in exts:
                if i in url:
                    print(url)


def DownloadDeps(dat, pkg, rec=None, opt=None):
    if opt:
        print('required, recommneded, and optional')
    if rec:
        print('required and recommended')
    
    print(dat[pkg])


def DepsList(dat, pkg, rec=None, opt=None):
    if not pkg in dat:
        print('{0} "{1}"'.format(errors[1], pkg))
        exit()

    print('list packages')


def parserFunction(dat):
    parser = argparse.ArgumentParser(description='This script takes a valid BLFS package as an input and either lists '
                                                 'the dependencies, or downloads the necessary packages ', prog='deps.py')
    parser.add_argument('-a', '--all', help='Will download ALL packages. Uses a lot of time and '
                                            'space', action='store_true')
    parser.add_argument('-c', '--commands', metavar='PACKAGE', help='List installation commands for a given package.',
                        default=False)
    parser.add_argument('-d', '--download', help='Download given BLFS package', metavar='PACKAGE')
    parser.add_argument('-l', '--list', metavar='PACKAGE', help='List dependencies instead of downloading.',
                        default=False)
    parser.add_argument('-o', '--optional', help='Allow installation of optional packages.', action='store_true')
    parser.add_argument('-r', '--recommended', help='Allow installation of recommended packages.',
                        default=False, action='store_true')
    args = parser.parse_args()

    if args.download:
        DownloadDeps(dat, args.download, args.recommended, args.optional)
    elif args.list:
        DepsList(dat, args.list, args.recommended, args.optional)
    elif args.commands:
        ListCommands(dat, args.commands)
    elif args.all:
        DownloadAll(dat, extensions)
    else:
        parser.print_help()
        

if not os.path.exists('dependencies.json'):
    print(errors[0])
    exit()

with open('dependencies.json', 'r+') as scheme:
    data = json.load(scheme)

parserFunction(data)
