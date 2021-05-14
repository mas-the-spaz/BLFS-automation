import argparse
import json
import os
import wget
import tarfile
import zipfile
import subprocess

''''
Todo:
1) basic autocomplete checker (maybe just for version number)
9) rename repo to 'BLFS-automation-script'
10) add comments
'''

default_download_path = '/blfs_sources/'
# change above line for the default download location for the packages

messages = ["Dependencies.json not found! Try running 'bootstrap.py' to rebuild the dependency database",
            "no dependencies found for ", "Download directory not found - creating one.",
            "Creation of download directory failed!", "Successfully created directory.",
            "Found existing download directory. Proceeding...", "Install packages in this order:",
            "Downloaded file could not be decompressed!"]

extensions = ['.bz2', '.tar.xz', '.zip', '.tar.gz', '.patch', '.tgz']


def CheckDir():  # download directory housekeeping function
    if not os.path.exists(default_download_path):
        print(messages[2])
        try:
            os.mkdir(default_download_path, 0o755)
        except OSError:
            print(messages[3])
            exit(1)
        else:
            print(messages[4])
    else:
        print(messages[5])
    os.chdir(default_download_path)
    return


def FtpUrlCheck(UrlsList):  # removes ftp links from url list, but only if they ar duplicates
    NewList = []
    i = 0
    while i < len(UrlsList):
        if (i % 2) == 0:
            NewList.append(UrlsList[i])
        elif not 'ftp://' in UrlsList[i]:
            print(UrlsList[i])
            NewList.append(UrlsList[i])
        i += 1
    return NewList


def ListCommands(dat, pkg):  # list the installation commands for a given BLFS package
    CommandsList = []
    if not pkg in dat:
        print('{0} "{1}"'.format(messages[1], pkg))
        exit()
    for command in dat[pkg]['Commands']: 
        CommandsList.append(command)
    return CommandsList


def BuildPkg(dat, pkg, exts):  # install a given BLFS package on the system
    DownloadDeps(dat, [pkg], exts)
    FileToExtract = dat[pkg]['url'][0]
    if tarfile.is_tarfile(os.path.basename(FileToExtract)):
        with tarfile.open(os.path.basename(FileToExtract), "r") as tar_ref:
            tar_ref.extractall()
            os.chdir(tar_ref.getnames()[0])

    if zipfile.is_zipfile(os.path.basename(FileToExtract)):
        with zipfile.ZipFile(os.path.basename(FileToExtract), "r") as zip_ref:
            zip_ref.extractall()
            os.chdir(tar_ref.getnames()[0])

    commands = ListCommands(dat, pkg)
    for command in commands:
        print(command)
    # for each command, pipe into bash


def DownloadDeps(dat, dlList, exts):  # download all urls in dlList (can be all urls or some dependencies)
    CheckDir()
    for package in dlList:
        if package in dat:
            NonFtp = FtpUrlCheck(dat[package]['url'])
            for url in NonFtp:
                for i in exts:
                    if i in url:
                        if not os.path.isfile(os.path.basename(url)):
                            print('\nDownloading: {0}\n'.format(url))
                            wget.download(url, os.path.basename(url))
                        else:
                            print('{} already has been downloaded'.format(os.path.basename(url)))


def DepsList(dat, pkg, rec=None, opt=None):  # lists all dependencies (can be required, recommended, and/or optional)
    if not pkg in dat:
        print('{0} "{1}"'.format(messages[1], pkg))
        exit()
    else:
        __types = ['required']
    if rec:
        __types.append('recommended')
    elif opt: 
        __types.extend(['recommended', 'optional'])
    return GetChild(dat, [pkg], __types)


def GetChild(dat, PkgList, types):  # recursively lists all dependencies for a given package
    for pkg in PkgList:
        if pkg in dat:
            for index in types:
                for dep in dat[pkg]['Dependencies'][index]:
                    if not dep in PkgList:  # prevents circular dependency problems
                        PkgList.append(dep)
    return PkgList


def Output(lst, reverse):  # outputs thing to stdout
    if reverse:
        lst.reverse()
    else:
        pass
    for thing in lst:
        print(thing)


def parserFunction(dat):  # main parser function
    parser = argparse.ArgumentParser(description='This script takes a valid BLFS package as an input and either lists '
                                                 'the dependencies, or downloads the necessary packages. (Input is '
                                                 'cAsE sEnsItIvE)',
                                     prog='deps.py')
    parser.add_argument('-a', '--all', help='Will download ALL packages. Uses a lot of time and '
                                            'space', action='store_true')
    parser.add_argument('-b', '--build', help='Install a given Package', metavar='PACKAGE', default=False)
    parser.add_argument('-c', '--commands', metavar='PACKAGE', help='List installation (without installing) commands '
                                                                    'for a given package.', default=False)
    parser.add_argument('-d', '--download', help='Download given BLFS package', metavar='PACKAGE')
    parser.add_argument('-l', '--list', metavar='PACKAGE', help='List dependencies instead of downloading.',
                        default=False)
    parser.add_argument('-o', '--optional', help='Allow installation of optional packages.', action='store_true')
    parser.add_argument('-r', '--recommended', help='Allow installation of recommended packages.', action='store_true')
    args = parser.parse_args()

    if args.download:
        DownloadDeps(dat, DepsList(dat, args.download, args.recommended, args.optional), extensions)
    elif args.list:
        print(messages[6])
        Output(DepsList(dat, args.list, args.recommended, args.optional), True)
    elif args.commands:
        Output(ListCommands(dat, args.commands), False)
    elif args.all:
        DownloadDeps(dat, dat, extensions)
    elif args.build:
        BuildPkg(dat, args.build, extensions)
    else:
        parser.print_help()


if not os.path.exists('dependencies.json'):
    print(messages[0])
    exit()

with open('dependencies.json', 'r+') as scheme:
    data = json.load(scheme)

parserFunction(data)
