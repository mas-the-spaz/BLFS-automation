from pathlib import Path

DEFAULT_BASE_URL = 'https://www.linuxfromscratch.org/blfs/view/stable/'
SYSTEMD_BASE_URL = 'https://www.linuxfromscratch.org/blfs/view/stable-systemd/' 
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0'
}

ROOT_PATH = Path(__file__).resolve().parent.parent

DOWNLOAD_PATH = ROOT_PATH / 'blfs_sources/'

INSTALLED_PATH = ROOT_PATH / '.installed_log'

EXCEPTIONS = ['Xorg Libraries', 'Xorg Applications',
              'Xorg Fonts', 'Xorg Legacy']

EXTENSIONS = ['.bz2', '.tar.xz', '.zip', '.tar.gz', '.patch', '.tgz']

CIRC_EXCEPTIONS = ['cups-filters-1.28.7']

DB_FILENAME = 'lfs-deps-11.3'

# database value types
class DbTypes:
    NAME        = 'name'
    URL         = 'url'
    DEPS        = 'deps'
    REQUIRED    = 'required' 
    RECOMMENDED = 'recommended'
    OPTIONAL    = 'optional'
    COMMANDS    = 'commands'
    HASHES      = 'hashes'
    KCONF       = 'kconf'
    TYPE        = 'pkg_type'
