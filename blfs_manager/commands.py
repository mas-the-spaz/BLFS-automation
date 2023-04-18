import tarfile
import zipfile
import os
import logging
from shutil import rmtree
import wget
from termcolor import colored

from .define import DbTypes, ROOT_PATH, EXCEPTIONS, EXTENSIONS, CIRC_EXCEPTIONS, DOWNLOAD_PATH, INSTALLED_PATH
from .utils import run_cmd, md5_check, safe_extract, rlinput, check_dir

class Commands(object):
    """Class to handle installation of BLFS packages.

    Args:
        database (dict): Dictionary containing information on BLFS packages.
        installed (list): List of installed BLFS packages.

    Attributes:
        database (dict): Dictionary containing information on BLFS packages.
        installed (list): List of installed BLFS packages.

    """

    def __init__(self, database, installed):
        """Initializes Commands with a database of BLFS packages and a list of installed packages.

        Args:
            database (dict): Dictionary containing information on BLFS packages.
            installed (list): List of installed BLFS packages.

        """
        self.database = database
        self.installed = installed
    
    def write_installed_log(self):
        """Writes the list of installed packages to a logfile."""
        with open(INSTALLED_PATH, 'w') as install_file:
            for i in self.installed:
                install_file.write(f'{i}\n')
    
    def cleanup(self, signum, frame):
        """Cleans up installation when the user interrupts it using the keyboard interrupt (ctrl-c).

        Args:
            signum (int): The signal number.
            frame (object): The current stack frame.

        """
        os.chdir(ROOT_PATH)
        if os.path.exists(self.package_dir):
            rmtree(self.package_dir)

        logging.error(colored('Installation interrupted - exiting.', 'red'))
        self.write_installed_log()
        exit(1)

    def check_pkg_status(self, pkg, kconf=False):
        """Checks the status of the given package and logs any relevant information.

        Args:
            pkg (str): The name of the package to check.
            kconf (bool): If True, logs kernel configuration information.

        """
        if self.database[pkg][DbTypes.TYPE] != 'BLFS':
            logging.info(f'"{pkg}" is not a BLFS package, you can download it at {self.database[pkg][DbTypes.URL][0]}')
        if kconf:
            if self.database[pkg][DbTypes.KCONF]:
                logging.info('This package requires some kernel configuration before installation.\n')
                for conf in self.database[pkg][DbTypes.KCONF]:
                    logging.info(f'{conf}\n')

    def search(self, pkg):
        """Searches for the given package in the database and logs any relevant information.

        Args:
            pkg (str): The name of the package to search for.

        """
        if len(pkg) < 3:
            logging.error(colored('The inputted value needs to be at least 3 characters.', 'red'))
            exit(1)
        if pkg in self.database:
            logging.info(f'"{pkg}" package exists in database.')
            # add query if it should install it
            return
        logging.info(colored(f'"{pkg}" package not found in database, but we found similar ones.\n', "blue"))
        for item in self.database.keys():
            if pkg.lower() in item.lower():
                logging.info(item)
        exit(0)

    def list_commands(self, pkg):
        """Lists the installation commands for a given BLFS package.

        Args:
            pkg (str): The name of the package to list commands for.

        Returns:
            list: A list of the installation commands for the given package.

        """
        self.search(pkg)
        self.check_pkg_status(pkg, kconf=True)

        commands_list = list(map(lambda x: x, self.database[pkg][DbTypes.COMMANDS]))
        return commands_list

    def build_pkg(self, pkg, force=None):
        """
        Installs a given BLFS package on the system.

        Args:
            pkg (str): The name of the package to install.
            force (bool, optional): A flag to force the installation even if the package is already installed.

        Returns:
            None
        """
        self.search(pkg)
        pkg_queue = self.list_deps(pkg)
        self.download_deps(pkg_queue)
        for package in pkg_queue:
            self.install_package(package, force)
    
    def install_package(self, pkg, force):
        """
        Installs a BLFS package on the system.

        Args:
            pkg (str): The name of the package to install.
            force (bool): A flag to force the installation even if the package is already installed.

        Returns:
            None
        """
        # check if blfs package or external
        if pkg in self.installed and not force:
            logging.info(colored(f'"{pkg}" has already been installed - skipping', "blue"))
            return
        else:
            if pkg not in EXCEPTIONS:
                logging.info(colored(f'Installing {pkg}.\n', "green"))
                file_to_extract = self.database[pkg][DbTypes.URL][0]
                file_basename = os.path.basename(file_to_extract)
                if tarfile.is_tarfile(file_basename):
                    with tarfile.open(file_basename, 'r') as tar_ref:
                        safe_extract(tar_ref)
                        os.chdir(tar_ref.getnames()[0].split('/', 1)[0])

                if zipfile.is_zipfile(file_basename):
                    with zipfile.ZipFile(file_basename, 'r') as zip_ref:
                        zip_new_dir = os.path.splitext(file_basename)[0]
                        logging.info(zip_new_dir)
                        zip_ref.extractall(zip_new_dir)
                        os.chdir(zip_new_dir)
            else:
                pkg = pkg.replace(' ', '_')
                if not os.path.exists(DOWNLOAD_PATH + pkg):
                    os.mkdir(pkg, 0o755)
                    os.chdir(pkg)

            commands = self.list_commands(pkg)
            self.package_dir = os.getcwd()
            for command in commands:
                install_query = input(f'Should I run \n"{command}"\n <Y/n/m (modify)>')
                if install_query.lower()[:1] == 'n':
                    pass
                elif install_query.lower()[:1] == 'm':
                    modified_cmd = rlinput('Custom command to run: ', command)
                    run_cmd(modified_cmd)
                elif install_query.lower()[:1] == '' or 'y':
                    run_cmd(command)
            if not force:
                self.installed.append(pkg)
            os.chdir(DOWNLOAD_PATH)
            rmtree(self.package_dir)
            logging.info(f'succesfully installed {pkg}!')

    def download_deps(self, dlist):
        """Downloads all urls in dlist (can be all urls or just some dependencies).

        Args:
            dlist (list): A list of package dependencies to download.

        Returns:
            None

        Raises:
            None

        """
        check_dir()
        for pkg in dlist:
            if pkg in self.database and pkg not in EXCEPTIONS:
                for url, hash_val in zip(self.database[pkg][DbTypes.URL], self.database[pkg][DbTypes.HASHES]):
                    self.check_pkg_status(pkg)
                    for ext in EXTENSIONS:
                        if ext in url:
                            filename = os.path.basename(url)
                            if not os.path.isfile(filename):
                                logging.info(colored(f'\nDownloading: {url}\n', "green"))
                                wget.download(url, filename)
                                print(f'\nSuccessfully downloaded {url}')
                                md5_check(filename, hash_val)
                            else:
                                logging.info(colored(f'{filename} already has been downloaded', "blue"))
            elif pkg in EXCEPTIONS:
                logging.info(f'"{pkg}" package must be installed manually.')
            else:
                logging.error(colored(f'Input needs to be at least 3 characters: "{pkg}"', "red"))

    def list_deps(self, pkg, rec=None, opt=None):
        """Lists all dependencies (can be required, recommended, and/or optional).

        Args:
            pkg (str): The name of the package to list dependencies for.
            rec (bool): Whether to list recommended dependencies.
            opt (bool): Whether to list optional dependencies.

        Returns:
            A list of dependencies.

        Raises:
            None

        """
        pkg_list = [pkg]
        if pkg not in self.database:
            self.search(pkg)
        else:
            if rec:
                pkg_list.extend([x for x in self.database[pkg]
                                [DbTypes.DEPS][DbTypes.RECOMMENDED]])
            elif opt:
                pkg_list.extend([x for x in self.database[pkg]
                                [DbTypes.DEPS][DbTypes.RECOMMENDED]])
                pkg_list.extend([x for x in self.database[pkg]
                                [DbTypes.DEPS][DbTypes.OPTIONAL]])

        for pkg_dep in pkg_list:
            if pkg_dep in self.database:
                for dep in self.database[pkg_dep][DbTypes.DEPS][DbTypes.REQUIRED]:
                    # prevents circular dependency problems
                    pkg_list[:] = [x for x in pkg_list if x != dep]
                    pkg_list.append(dep)
        # ensure that main package is last (insurance for circular dependency problem)
        pkg_list.insert(0, pkg_list.pop(pkg_list.index(pkg)))
        pkg_list.reverse()
        return pkg_list
