#!/usr/bin/python3

import wget
import argparse
import json
import os
import tarfile
import zipfile
import hashlib
import subprocess
import re
from shutil import rmtree
import signal

default_download_path = '/blfs_sources/'
# change above line for the default download location for the packages

script_path = os.getcwd()

exceptions = ['Xorg Libraries', 'Xorg Applications', 'Xorg Fonts', 'Xorg Legacy']

messages = ["Dependencies.json not found! Try running 'bootstrap.py' to rebuild the dependency database.\n",
            "The inputted value needs to be at least 3 characters.", "Download directory not found - creating one.\n",
            "Creation of download directory failed!\n", "Successfully created directory.\n",
            "Found existing download directory. Proceeding...", "Install packages in this order:\n",
            "Downloaded file could not be decompressed!\n",
            "A simple script to list, download, and install any valid BLFS package along with any dependencies.\n"
            "(Input is cAsE sEnsItIvE).\n",
            "Downloads ALL BLFS packages - uses a lot of time and space.\n", "Install a given Package on the system.\n",
            "List installation (without installing) commands for a given package.\n",
            "Downloads a given BLFS package along with all of its dependencies.\n",
            "Lists all of the dependencies for a given BLFS package in order of installation.\n",
            "Also list/download optional packages.\n",
            "Also list/download recommended packages.\n", "Downloaded file does not match the MD5 hash!\n",
            "This package requires some kernel configuration before installation.\n", 
            "is not a BLFS package, you can download it at", "Downloads and installs thegiven package with all of it's dependencies.\n",
            "Search for a given package.\n"]

extensions = ['.bz2', '.tar.xz', '.zip', '.tar.gz', '.patch', '.tgz']


def cleanup(signum, frame):
    os.chdir(script_path)
    with open('installed', 'w') as install_file:
        for i in installed:
            install_file.write('{}\n'.format(i))
    print('Installation interrupted - exiting.')
    exit(0)

signal.signal(signal.SIGINT, cleanup)


def check_dir():  # download directory housekeeping function
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


def change_dir(cmd):
    for i, w in enumerate(cmd):
        if w == 'cd':
            return cmd[i+1]
    return ''


def MD5_check(hash, file):  # verify file hash
    file_hash = hashlib.md5(open(file,'rb').read()).hexdigest()
    if hash != file_hash:
        print(messages[16])
        os.remove(file)
        exit


def search(dat, pkg):
    if len(pkg) < 3:
        print(messages[1])
        exit()
    if pkg in dat:
        print('{} package exists in database.'.format(pkg))
        return
    print('"{}" package not found in database.'.format(pkg))
    for item in dat.keys():
        if pkg.lower() in item.lower():
            print('Did you mean {}?'.format(item))
    exit()


def everything(dat, pkg, rec=None, opt=None):  # downloads and builds given package along with all of its dependencies
    pkg_list = list_deps(dat, pkg, rec, opt)
    for item in pkg_list:
        if item in dat:
            print('Installing {}.\n'.format(item))
            #build_pkg(dat, item)
        else:
            print('"{}" package not found in database - skipping to the next package'.format(item))


def list_commands(dat, pkg):  # list the installation commands for a given BLFS package
    search(dat, pkg)
    if dat[pkg]['type'] != 'BLFS':  # if this is an external package
        print('"{0}" {1} {2}'.format(pkg, messages[18], dat[pkg]['url'][0]))
        exit()
    elif dat[pkg]['kconf']:
        print(messages[17])
        for conf in dat[pkg]['kconf']:
            print('{}\n'.format(conf))

    print('Listing commands for {}\n'.format(pkg))
    commands_list = list(map(lambda x: x, dat[pkg]['Commands']))
    return commands_list


def build_pkg(dat, pkg):  # install a given BLFS package on the system
    search(dat, pkg)
    download_deps(dat, [pkg], extensions)
    if pkg in installed:
        print('\33[31m{} has already been installed - skipping\33[0m'.format(pkg))
        return
    else:
        if pkg not in exceptions:
            file_to_extract = dat[pkg]['url'][0]
            if tarfile.is_tarfile(os.path.basename(file_to_extract)):
                with tarfile.open(os.path.basename(file_to_extract), 'r') as tar_ref:
                    tar_ref.extractall()
                    os.chdir(tar_ref.getnames()[0].split('/', 1)[0])

            if zipfile.is_zipfile(os.path.basename(file_to_extract)):
                with zipfile.ZipFile(os.path.basename(file_to_extract), 'r') as zip_ref:
                    print(os.path.splitext(os.path.basename(file_to_extract))[0])
                    zip_ref.extractall(os.path.splitext(os.path.basename(file_to_extract))[0])
                    os.chdir(os.path.splitext(os.path.basename(file_to_extract))[0])
        else:
            _pkg = pkg.replace(' ', '_')
            if not os.path.exists(default_download_path + _pkg):
                os.mkdir(_pkg)
                os.chdir(_pkg)

        commands = list_commands(dat, pkg)
        package_dir = os.getcwd()
        for command in commands:
            install_query = input('\33[32mShould I run "{}"? <y/n>\33[0m\n'.format(command))
            if install_query.lower() == 'y':
                print('running {}'.format(command))
                subprocess.call(['/bin/sh', '-c', command])  # output command to shell
                os.chdir(os.getcwd() + '/' + change_dir(re.sub('\s+', ' ', command).split()))
            else:
                pass
        installed.append(pkg)
        os.chdir(default_download_path)
        rmtree(package_dir)


def download_deps(dat, dlist, exts):  # download all urls in dlist (can be all urls or just some dependencies)
    check_dir()
    for pkg in dlist:
        if pkg in dat and pkg not in exceptions:
            for index, url in enumerate(dat[pkg]['url']):
                if dat[pkg]['type'] != 'BLFS':
                    print('"{0}" {1} {2}'.format(pkg, messages[18], dat[pkg]['url'][0]))
                    exit()
                for i in exts:
                    if i in url:
                        if not os.path.isfile(os.path.basename(url)):
                            print('\n\33[32mDownloading: {0}\33[0m\n'.format(url))
                            wget.download(url, os.path.basename(url))
                            print('\n')
                            if index > len(dat[pkg]['Hashes']):
                                MD5_check(dat[pkg]['Hashes'][index], os.path.basename(url))
                        else:
                            print('\33[31m{} already has been downloaded\33[0m'.format(os.path.basename(url)))
        elif pkg in exceptions:
            print('{} package must be installed manually.'.format(pkg))
        else:
            print('{0} "{1}"'.format(messages[1], pkg))


def list_deps(dat, pkg, rec=None, opt=None):  # lists all dependencies (can be required, recommended, and/or optional)
    types = []
    if not pkg in dat:
        search(dat, pkg)
    else:
        types.append('required')
    if rec:
        types.append('recommended')
    elif opt:
        types.extend(['recommended', 'optional'])
    return get_child(dat, [pkg], pkg, types)


def get_child(dat, pkg_list, org_pkg, types):  # recursively lists all dependencies for a given package
    duplicate_list = []
    for pkg in pkg_list:
        if pkg in dat:
            for index in types:
                for dep in dat[pkg]['Dependencies'][index]:
                    if not dep in pkg_list:  # prevents circular dependency problems
                        pkg_list.append(dep)
                    else:  # if it is, i need to make sure it gets put at the top of the list
                        duplicate_list.append(dep)
    print(pkg_list)
    print(duplicate_list)
    pkg_list.extend(duplicate_list)
    pkg_list.reverse()
    pkg_list = list(dict.fromkeys(pkg_list))
    pkg_list.append(pkg_list.pop(pkg_list.index(org_pkg)))
    # make sure that the original package is at the end of the list (will be installed last)
    print(pkg_list)
    return pkg_list


def output(lst, reverse):  # output function
    if reverse:
        print(messages[6])
    else:
        pass
    for thing in lst:
        print(thing)


def parser(dat):  # main parser function
    parser = argparse.ArgumentParser(description=messages[8], prog='deps.py')
    parser.add_argument('-a', '--all', help=messages[9], action='store_true')
    parser.add_argument('-b', '--build', help=messages[10], metavar='PACKAGE', default=False)
    parser.add_argument('-c', '--commands', help=messages[11], metavar='PACKAGE', default=False)
    parser.add_argument('-d', '--download', help=messages[12], metavar='PACKAGE')
    parser.add_argument('-e', '--everything', help=messages[19], metavar='PACKAGE')
    parser.add_argument('-l', '--list', help=messages[13], metavar='PACKAGE', default=False)
    parser.add_argument('-o', '--optional', help=messages[14], action='store_true')
    parser.add_argument('-r', '--recommended', help=messages[15], action='store_true')
    parser.add_argument('-s', '--search', help=messages[20], metavar='PACKAGE')
    args = parser.parse_args()

    if args.download:
        download_deps(dat, list_deps(dat, args.download, args.recommended, args.optional), extensions)
    elif args.everything:
        everything(dat, args.everything, args.recommended, args.optional)
    elif args.list:
        output(list_deps(dat, args.list, args.recommended, args.optional), True)
    elif args.commands:
        output(list_commands(dat, args.commands), False)
    elif args.all:
        download_deps(dat, dat, extensions)
    elif args.build:
        build_pkg(dat, args.build)
    elif args.search:
        search(dat, args.search)
    else:
        parser.print_help()

    os.chdir(script_path)
    with open('installed', 'w') as install_file:
        for i in installed:
            install_file.write('{}\n'.format(i))


if not os.path.exists('dependencies.json'):
    print(messages[0])
    exit()

with open('dependencies.json', 'r') as scheme:
    data = json.load(scheme)

if not os.path.exists('installed'):
    with open('installed', 'w') as f:
        f.write('')

with open('installed', 'r') as i:
    installed = i.readlines()
    installed = [i.strip() for i in installed]

parser(data)
