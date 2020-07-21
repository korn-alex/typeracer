# if __name__ == "__main__":
#     from sys import path
#     from pathlib import Path
#     path.insert(0, str(Path.cwd()))
import requests as rq
from subprocess import Popen, PIPE
import sys, os
from pathlib import Path
import re
from zipfile import ZipFile
from toolbox.web import Downloader
import platform
import json

CURRENT_OS = platform.system()

print('DEBUG INFO')
print('-'*80)
print(f'Operating System: {CURRENT_OS}')
frozen = 'not'
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
print( 'we are',frozen,'frozen')
print( 'bundle dir is', bundle_dir )
print( 'sys.argv[0] is', sys.argv[0] )
print( 'sys.executable is', sys.executable )
print( 'os.getcwd is', os.getcwd() )
print( 'Path.cwd is', Path.cwd() )
print('-'*80)

def get_chrome_version():
    print('Checking Chrome version for chromedriver')
    if CURRENT_OS == 'Windows':
        cmd = Popen(['powershell.exe','(Get-Item "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe").VersionInfo'], stdout=PIPE)
    elif CURRENT_OS == 'Linux':
        cmd = Popen(['/usr/bin/chromium-browser','--version'], stdout=PIPE)
    else:
        raise NotImplementedError(f'Your operating system {CURRENT_OS} is not supported.')
    lines = cmd.stdout.readlines()
    version = None
    for line in lines:
        v = re.search(r'\d+', line.decode('utf-8'))
        if v:
            version = v.group()
            print(f'Chrome version: {version}')
    if not version:
        raise FileNotFoundError('Chrome not found, install Chrome first or check config.json')
    return version

def get_chromedriver_version():
    print('Checking chromedriver version')
    if CURRENT_OS == 'Windows':
        cmd = Popen(['powershell.exe','.\chromedriver.exe -v'], stdout=PIPE)
    elif CURRENT_OS == 'Linux':
        cmd = Popen(['chromedriver', '--version'], stdout=PIPE)
    else:
        print(f'You Operating System {CURRENT_OS} is not supported.')
        raise NotImplementedError        
    lines = cmd.stdout.readlines()
    version = None
    for line in lines:
        v = re.match(r'ChromeDriver (\d+)', line.decode('utf-8'))
        if v:
            version = v.group(1)
            print(f'Chromedriver version: {version}')
    if not version:
        print('Version for chromedriver not found.')
        raise FileNotFoundError
    return version

def download_chromedriver(version):
    print(f'Downloading chromedriver version:{version}')
    v_url = f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version}'
    response = rq.get(v_url)
    latest_chrome_version = response.content.decode('utf-8')
    if CURRENT_OS == 'Windows':
        d_url = f'https://chromedriver.storage.googleapis.com/{latest_chrome_version}/chromedriver_win32.zip'
    elif CURRENT_OS == 'Linux':
        d_url = f'https://chromedriver.storage.googleapis.com/{latest_chrome_version}/chromedriver_linux64.zip'
    d = Downloader()
    d.download(d_url)
    _unzip_chromedriver()

def _unzip_chromedriver():
    print('Extracting chromedriver zip')
    if CURRENT_OS == 'Windows':
        driver_name = 'chromedriver_win32.zip'
        with ZipFile(driver_name, mode='r') as z:
            z.extractall()
    elif CURRENT_OS == 'Linux':
        driver_name = 'chromedriver_linux64.zip'
        with ZipFile(driver_name, mode='r') as z:
            z.extractall()
        Popen(['chmod','+x', 'chromedriver'])
    else:
        print(f'You Operating System {CURRENT_OS} is not supported.')
        raise NotImplementedError
    
    print('Removing zip File')
    cdz = Path.cwd() / driver_name
    if cdz.is_file():
        cdz.unlink()

def check_chromedriver():
    """
    Checks for chromedriver.exe in current working directory.
    Compares compatability with Chrome and downloads a new version
    if necessary.
    """
    if CURRENT_OS == 'Windows':
        cd_file = 'chromedriver.exe'
    elif CURRENT_OS == 'Linux':
        cd_file = 'chromedriver'
    else:
        print(f'You Operating System {CURRENT_OS} is not supported.')
        raise NotImplementedError
    cd = Path(cd_file)
    if cd.is_file():
        cdv = get_chromedriver_version()
        cv = get_chrome_version()
        if cdv != cv:
            print('Chromedriver outdated, downloading new version.')
            download_chromedriver(cv)
            print('Done')
        else:
            print('Chromedriver is up to date')
    else:
        cv = get_chrome_version()
        print('Chromedriver not found.')
        download_chromedriver(cv)
        print('Done')

def get_config() -> dict:
    """Dict from `config.json`.
    `chrome_path=path`
    """
    config_path = Path.cwd() / 'config.json'
    try:
        with open(config_path,'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        _create_config()
        with open(config_path,'r') as f:
            config = json.load(f)
    return config

def _create_config():
    if CURRENT_OS == 'Windows':
        config = {'chrome_path':'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'}
    elif CURRENT_OS == 'Linux':
        config = {'chrome_path':'/usr/bin/chromium-browser'}
    config_file = Path.cwd() / 'config.json'
    with open(config_file,'w') as f:
        json.dump(config, f)
    print('Created config')

if __name__ == "__main__":
    # check_chromedriver()
    get_config()