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
import signal
import readline
from termcolor import colored
from shutil import rmtree

default_download_path = '/blfs_sources/'
# change above line for the default download location for the packages

SCRIPT_PATH = os.getcwd()

EXCEPTIONS = ['Xorg Libraries', 'Xorg Applications', 'Xorg Fonts', 'Xorg Legacy']

MESSAGES = ["Dependencies.json not found! Try running 'bootstrap.py' to rebuild the dependency database.\n",
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
            "Search for a given package.\n", "Force package installation even though it is already installed\n"]

EXTENSIONS = ['.bz2', '.tar.xz', '.zip', '.tar.gz', '.patch', '.tgz']

CIRC_EXCEPTIONS = ['cups-filters-1.28.7']

def cleanup(signum, frame):  # ctrl-c handler
    os.chdir(SCRIPT_PATH)
    if os.path.exists(PACKAGE_DIR):
        rmtree(PACKAGE_DIR)

    with open('.installed', 'w') as install_file:
        for i in installed:
            install_file.write('{}\n'.format(i))
    print(colored('Installation interrupted - exiting.', 'red'))
    exit(1)

signal.signal(signal.SIGINT, cleanup)


def rlinput(prompt, prefill=''):  # makes command modifiable
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()


def check_dir():  # download directory housekeeping function
    if not os.path.exists(default_download_path):
        print(MESSAGES[2])
        try:
            os.mkdir(default_download_path, 0o755)
        except OSError:
            print(MESSAGES[3])
            exit(1)
        else:
            print(MESSAGES[4])
    else:
        print(MESSAGES[5])
    os.chdir(default_download_path)
    return


def change_dir(cmd):  # change dir when command contains 'cd'
    for i, w in enumerate(cmd):
        if w == 'cd':
            return cmd[i+1]
    return ''


def MD5_check(file, hash):  # verify file hash
    file_hash = hashlib.md5(open(file,'rb').read()).hexdigest()
    if hash != file_hash:
        print(MESSAGES[16])
        os.remove(file)
        exit()


def cmd_run(command):  # run command in shell
    print(colored('Running {}'.format(command), 'green'))
    subprocess.call(['/bin/sh', '-c', command])  # output command to shell
    os.chdir(os.getcwd() + '/' + change_dir(re.sub('\s+', ' ', command).split()))


def output(lst, reverse):  # output function
        if reverse:
            print(MESSAGES[6])
        else:
            pass
        for thing in lst:
            print(thing)



class Actions(object):
    def __init__(self, database):
        self.database = database

    def search(self, pkg):
        if len(pkg) < 3:
            print(MESSAGES[1])
            exit()
        if pkg in self.database:
            print('{} package exists in database.'.format(pkg))
            return
        print(colored('"{}" package not found in database.'.format(pkg), "red"))
        for item in self.database.keys():
            if pkg.lower() in item.lower():
                print('Did you mean {}?'.format(item))
        exit()

    def list_commands(self, pkg):  # list the installation commands for a given BLFS package
        self.search(pkg)
        if self.database[pkg]['type'] != 'BLFS':  # if this is an external package
            print('"{0}" {1} {2}'.format(pkg, MESSAGES[18], self.database[pkg]['url'][0]))
            exit()
        elif self.database[pkg]['kconf']:
            print(MESSAGES[17])
            for conf in self.database[pkg]['kconf']:
                print('{}\n'.format(conf))

        print(colored('Listing commands for {}\n'.format(pkg), "green"))
        commands_list = list(map(lambda x: x, self.database[pkg]['Commands']))
        return commands_list


    def build_pkg(self, pkg, force):  # install a given BLFS package on the system
        self.search(pkg)
        self.download_deps([pkg], EXTENSIONS)
        if pkg in installed and not force:
            print(colored('{} has already been installed - skipping'.format(pkg), "red"))
            return
        else:
            if pkg not in EXCEPTIONS:
                print(colored('Installing{}.\n'.format(pkg), "green"))
                file_to_extract = self.database[pkg]['url'][0]
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
                    os.mkdir(_pkg, 0o755)
                    os.chdir(_pkg)

            commands = self.list_commands(pkg)
            global PACKAGE_DIR
            PACKAGE_DIR = os.getcwd()
            for command in commands:
                install_query = input('Should I run "{}"? <Y/n/m (to modify)>'.format(command))
                if install_query.lower() == 'n':
                    pass
                elif install_query.lower() == 'm':
                    modified_cmd = rlinput('Custom command to run: ', command)
                    cmd_run(modified_cmd)
                elif install_query.lower() == '' or 'y':
                    cmd_run(command)
            if not force:
                installed.append(pkg)
            os.chdir(default_download_path)
            rmtree(PACKAGE_DIR)


    def download_deps(self, dlist, exts):  # download all urls in dlist (can be all urls or just some dependencies)
        check_dir()
        for pkg in dlist:
            if pkg in self.database and pkg not in EXCEPTIONS:
                for _, url in enumerate(self.database[pkg]['url']):
                    if self.database[pkg]['type'] != 'BLFS':
                        print('"{0}" {1} {2}'.format(pkg, MESSAGES[18], self.database[pkg]['url'][0]))
                        exit()
                    for i in exts:
                        if i in url:
                            if not os.path.isfile(os.path.basename(url)):
                                print(colored('\nDownloading: {0}\n'.format(url), "green"))
                                wget.download(url, os.path.basename(url))
                                print('\n')
                                for foo in list(zip(self.database[pkg]["url"], self.database[pkg]['Hashes'])):
                                    MD5_check(os.path.basename(foo[0]), foo[1])
                            else:
                                print(colored('{} already has been downloaded'.format(os.path.basename(url), "red")))
            elif pkg in EXCEPTIONS:
                print('{} package must be installed manually.'.format(pkg))
            else:
                print(colored('{0} "{1}"'.format(MESSAGES[1], pkg), "red"))


    def list_deps(self, pkg, rec=None, opt=None):  # lists all dependencies (can be required, recommended, and/or optional)
        pkg_list = [pkg]
        if not pkg in self.database:
            self.search(pkg)
        else:    
            if rec:
                pkg_list.extend([x for x in self.database[pkg]['Dependencies']['recommended']])
            elif opt:
                pkg_list.extend([x for x in self.database[pkg]['Dependencies']['recommended']])
                pkg_list.extend([x for x in self.database[pkg]['Dependencies']['optional']])

        for p in pkg_list:
            if p in self.database:
                for dep in self.database[p]['Dependencies']['required']:
                    pkg_list[:] = [x for x in pkg_list if x != dep] # prevents circular dependency problems
                    pkg_list.append(dep)                          
        pkg_list.insert(0, pkg_list.pop(pkg_list.index(pkg)))  # ensure that main package is last (insurance for circular dependency problem)
        pkg_list.reverse()
        return pkg_list


def parser(dat):  # main parser function
    parser = argparse.ArgumentParser(description=MESSAGES[8], prog='deps.py')
    parser.add_argument('-a', '--all', help=MESSAGES[9], action='store_true')
    parser.add_argument('-b', '--build', help=MESSAGES[10], metavar='PACKAGE', default=False)
    parser.add_argument('-c', '--commands', help=MESSAGES[11], metavar='PACKAGE', default=False)
    parser.add_argument('-d', '--download', help=MESSAGES[12], metavar='PACKAGE')
    parser.add_argument('-f', '--force', help=MESSAGES[21], action='store_true')
    parser.add_argument('-l', '--list', help=MESSAGES[13], metavar='PACKAGE', default=False)
    parser.add_argument('-o', '--optional', help=MESSAGES[14], action='store_true')
    parser.add_argument('-r', '--recommended', help=MESSAGES[15], action='store_true')
    parser.add_argument('-s', '--search', help=MESSAGES[20], metavar='PACKAGE')
    args = parser.parse_args()

    # init object with database and pass other info to specific functions
    action = Actions(dat)

    if args.download:
        action.download_deps(action.list_deps(args.download, args.recommended, args.optional), EXTENSIONS)
    elif args.list:
        output(action.list_deps(args.list, args.recommended, args.optional), True)
    elif args.commands:
        output(action.list_commands(args.commands), False)
    elif args.all:
        action.download_deps(dat, EXTENSIONS)
    elif args.build:
        action.build_pkg(args.build, args.force)
    elif args.search:
        action.search(args.search)
    else:
        parser.print_help()

    os.chdir(SCRIPT_PATH)
    with open('.installed', 'w') as install_file:
        for i in installed:
            install_file.write('{}\n'.format(i))


if __name__ == "__main__":
    try:
        with open('dependencies.json', 'r') as scheme:
            data = json.load(scheme)
    except FileNotFoundError:
        print(MESSAGES[0])
        exit()

    try:
        with open('.installed', 'r') as i:
            installed = [line.rstrip() for line in i]
    except FileNotFoundError:
        installed = []

    parser(data)
