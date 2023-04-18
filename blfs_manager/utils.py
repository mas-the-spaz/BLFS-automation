import readline
import hashlib
import os
import re
import subprocess
import json
import logging
from termcolor import colored


from .define import DOWNLOAD_PATH, DB_FILENAME, INSTALLED_PATH, SYSTEMD_BASE_URL, DEFAULT_BASE_URL
from .bootstrapper import bootstrap


def load_db(systemd=False):
    """
    Load the database file.

    Parameters:
        systemd (bool): A boolean indicating whether the database is for Systemd or not.

    Returns:
        dict: A dictionary containing the loaded JSON data from the database file.
    """
    if not os.path.exists(DB_FILENAME):
        logging.info('Downloading database, (this is a one time process)')
        bootstrap(SYSTEMD_BASE_URL if systemd else DEFAULT_BASE_URL)
    with open(DB_FILENAME, 'r') as database:
        return json.load(database)
        
def load_installed_log():
    """
    Load the list of installed packages.

    Returns:
        list: A list containing the names of installed packages.
    """
    try:
        with open(INSTALLED_PATH, 'r') as i:
            installed = [line.rstrip() for line in i]
    except FileNotFoundError:
        installed = []
    return installed


def rlinput(prompt, prefill=''):
    """
    Readline input with pre-filled text.

    Parameters:
        prompt (str): The input prompt.
        prefill (str): The text to pre-fill the input field.

    Returns:
        str: The user input string.
    """
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def check_dir():
    """
    Check if the download directory exists and create it if it doesn't.

    Returns:
        None
    """
    if not os.path.exists(DOWNLOAD_PATH):
        logging.debug('Download directory not found - creating one.\n')
        try:
            os.mkdir(DOWNLOAD_PATH, 0o755)
        except OSError:
            raise OSError('Creation of download directory failed!\n')
        else:
            logging.debug('Successfully created directory.\n')
    else:
        logging.debug('Found existing download directory. Proceeding...')
    os.chdir(DOWNLOAD_PATH)
    return


def change_dir(cmd):
    """
    Get the directory path from a 'cd' command.

    Parameters:
        cmd (str): The command string.

    Returns:
        str: The directory path.
    """
    for i, w in enumerate(cmd):
        if w == 'cd':
            return cmd[i+1]
    return ''


def md5_check(file, hash):
    """
    Check if a downloaded file's MD5 hash matches the expected hash.

    Parameters:
        file (str): The path to the downloaded file.
        hash (str): The expected MD5 hash.

    Returns:
        None
    Raises:
        OSError: If the downloaded file does not match the expected hash.
    """
    file_hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
    if hash != file_hash:
        os.remove(file)
        raise OSError('Downloaded file does not match the MD5 hash!\n')


def run_cmd(command):
    """
    Run a command in the shell.

    Parameters:
        command (str): The command string.

    Returns:
        None
    """
    logging.info(colored(f'Running {command}', 'green'))
    subprocess.call(['/bin/sh', '-c', command])  # output command to shell
    os.chdir(os.getcwd() + '/' + change_dir(re.sub('\s+', ' ', command).split()))


def is_within_directory(directory, target):
    """
    Check if a target path is within a specified directory.

    Parameters:
        directory (str): The directory path.
        target (str): The target path.

    Returns:
        bool: True if the target is within the directory, False otherwise.
    """
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    prefix = os.path.commonprefix([abs_directory, abs_target])
    return prefix == abs_directory


def safe_extract(tar, path=".", members=None, *, numeric_owner=False): 
    """
    Safely extract files from a tar archive.

    Parameters:
        tar (tarfile.TarFile): The TarFile object.
        path (str): The destination directory path.
        members (list): A list of TarInfo objects to extract.
        numeric_owner (bool): A flag indicating whether to use numeric owner values or not.

    Returns:
        None
    Raises:
        Exception: If there is an attempted path traversal in the TarFile.
    """                   
    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not is_within_directory(path, member_path):
            raise Exception("Attempted Path Traversal in Tar File")
    tar.extractall(path, members, numeric_owner=numeric_owner) 

def print_deps(pkg_list):
    """
    Print a list of packages to install in order.

    Parameters:
        pkg_list (list): A list of package names.

    Returns:
        None
    """
    logging.info(colored("Install packages in this order:\n", "green"))
    for pkg in pkg_list:
        logging.info(colored(pkg, attrs=['bold']))
    exit(0)

def print_commands(cmd_list, pkg):
    """
    Print a list of commands for a package.

    Parameters:
        cmd_list (list): A list of command strings.
        pkg (str): The package name.

    Returns:
        None
    """
    logging.info(colored(f'Listing commands for {pkg}\n', "green"))
    for i, command in enumerate(cmd_list):
        logging.info(f'Command {i+1}:')
        logging.info(colored(command, attrs=['bold']))
        print()
