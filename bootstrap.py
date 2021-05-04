import requests
from bs4 import BeautifulSoup as Bs4

baseUrl = 'https://github.com/mas-the-spaz/python-blfs.git'

res = requests.get(baseUrl, verify=False)
soup = Bs4(res.text, 'html.parser')
