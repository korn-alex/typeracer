# if __name__ == "__main__":
#     from sys import path
#     from pathlib import Path
#     path.insert(0, str(Path.cwd()))
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
from time import sleep
import sys
from pathlib import Path
import logging
from typeracer.utils import check_chromedriver, bundle_dir, get_config, CURRENT_OS
    

class ChromeBrowser:
    """
    fast and easy selenium browser initiated
    """
    logging.basicConfig(level=logging.INFO)
    def __init__(self):
        check_chromedriver()
        LOGGER.setLevel(logging.WARNING)
        self.driver = self._init_driver()

    def _init_driver(self):
        options = webdriver.chrome.options.Options()
        if CURRENT_OS == 'Windows':
            driver_path = Path.cwd() / 'chromedriver.exe'
        elif CURRENT_OS == 'Linux':
            driver_path = Path.cwd() / 'chromedriver'
        options.headless = False
        options.binary_location = get_config().get('chrome_path')
        # not working
        # options.add_argument('--no-sandbox')
        # options.add_argument('disable-infobars')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option("useAutomationExtension", False)
        # ignoring "handshake failed..." errors
        # options.add_argument('--ignore-certificate-errors')
        # options.add_argument('--ignore-ssl-errors')
        ext_ublock = Path(bundle_dir) / 'extensions' / 'ublock.crx'
        ext_darkreader = Path(bundle_dir) / 'extensions' / 'darkreader.crx'
        options.add_extension(ext_ublock)
        options.add_extension(ext_darkreader)
        # use this only if chromedriver is inlcuded as binary
        # with -add-data in pyinstaller
        # driver_path = Path(sys._MEIPASS) / 'chromedriver77.exe'
        return webdriver.Chrome(options=options, executable_path=str(driver_path))

    def navigate(self, url):
        current_url = self.driver.current_url
        if current_url != url:
            logging.info(f'Navigating to: {url}')
            self.driver.get(url)
        else:
            logging.info('Browser is currently on the same url')
            logging.info('Refreshing page')
            self.driver.get(url)

if __name__ == "__main__":
    print('')