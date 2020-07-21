if __name__ == "__main__":
    from sys import path
    from pathlib import Path
    path.insert(0, str(Path.cwd()))
import base64
import re
from time import sleep
from datetime import timedelta, datetime
from typeracer.browser import ChromeBrowser, NoSuchElementException, \
            NoSuchWindowException, WebDriverException, \
            Keys
from typeracer.database import DataBase
    
class TypeRacer(ChromeBrowser):
    """ Browser for TypeRacer statistics """
    rank_reg = re.compile('\d')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver.implicitly_wait(5)
        self.mode = None
        self.race_count = 0

    def sign_in(self, user):
        """Takes in tuple(user, pw)"""
        if user:
            print('Signing in')
            u = base64.b64decode(user[0]).decode('utf-8')
            p = base64.b64decode(user[1]).decode('utf-8')
            signed = False
            sign_in = self.driver.find_element_by_class_name('gwt-Anchor')
            while not signed:
                try:
                    sign_in.click()
                    break
                except:
                    pass
                sleep(1)
            user_box = self.driver.find_element_by_class_name('gwt-TextBox')
            user_box.click()
            user_box.send_keys(u)
            pw_box = self.driver.find_element_by_class_name('gwt-PasswordTextBox')
            pw_box.send_keys(p)
            pw_box.send_keys(Keys.ENTER)
            print('Signed in')
        else:
            print('Playing as guest')

    def read_stats_loop(self):
        """
        Looping self.read_stats
        until no Esceptions occur and every element
        is found.
        """
        print('waiting for stats...')
        print('')
        while True:
            try:
                stats = self.read_stats()
                return stats
            except:
                sleep(0.2)
                continue

    def read_stats(self) -> dict:
        """Returns stats dict."""
        t = self.driver.find_elements_by_class_name('tblOwnStatsNumber')
        quote = self.driver.find_element_by_class_name('remainingChars').text
        stats = {}
        wpm = int(t[0].text.split('wpm')[0].strip())
        minutes, seconds = t[1].text.split(':')
        time = int(seconds)+int(minutes)*60
        accuracy = float(t[2].text.replace('%',''))
        points = int(t[3].text)
        rank_raw = self.driver.find_element_by_class_name('rank').text
        self.race_count += 1
        if self.mode == 'race':
            rank = int(self.rank_reg.search(rank_raw).group())
        else:
            rank = None
        stats['wpm'] = wpm
        stats['time'] = time
        stats['accuracy'] = accuracy
        stats['points'] = points
        stats['quote'] = quote
        stats['mode'] = self.mode
        stats['rank'] = rank
        print(f'Race: {self.race_count:2d}')
        print(f'wpm: {wpm}')
        print(f'time: {time}')
        print(f'accuracy: {accuracy}')
        print(f'points: {points}')
        print(f'rank: {rank}')
        return stats
    
    def read_time(self):
        """ Reads remaining time. """
        time = self.driver.find_element_by_class_name('time').text
        print('remaining time: ', time)

    def wait_for_start(self):
        print('\rwaiting for game...', end='')
        practice_xp = '/html/body/div[1]/div/div[1]/div[1]/table/tbody/tr[2]/td[2]/div/div[1]/table/tbody/tr[3]/td/div/div/table/tbody/tr[2]/td[3]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div'
        race_xp = '/html/body/div[1]/div/div[1]/div[1]/table/tbody/tr[2]/td[2]/div/div[1]/div/table/tbody/tr[2]/td[3]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div'
        race_text = None
        practice_text = None
        lightlabel = None
        while not lightlabel: 
        # while not race_text or not practice_text:
            lightlabel = self.driver.find_element_by_class_name('lightLabel')
            # '//*[@id="gwt-uid-15"]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div'
            # '//*[@id="gwt-uid-31"]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div'
            practice_text = self._is_practice()
            sleep(0.5)
        self.mode = 'practice' if practice_text else 'race'
        print(f' mode: {self.mode}')
        
        # TODO
        # time = self.driver.find_element_by_class_name('timeDisplay')
        # time = self.driver.find_element_by_class_name('time')        
        # while time:
        #     time = self.driver.find_elements_by_class_name('time')
        #     remaining = time[0].text
        #     print(f'\rstart in {remaining:2s}', end='')

    def _is_practice(self):
        try:
            # race_text = self.driver.find_element_by_xpath('//*/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div')
            race_text = self.driver.find_element_by_xpath('//*/span[@unselectable="on"]')
        except Exception as e:
            # print(e)
            pass
        try:
            practice_text = self.driver.find_element_by_xpath('//*/tr[2]/td[2]/div/div[1]/table/tbody/tr[3]/td/div/div/table/tbody/tr[2]/td[3]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div')
            return practice_text
        except Exception as e:
            # print(e)
            pass
        # mode = self.driver.find_element_by_class_name('gameStatusLabel')
        # mode = self.driver.find_element_by_class_name('room-title')
        # return mode.text

def show_stats(db: DataBase):
    """Prints stats"""
    races = db.count_races()
    db.c.execute("SELECT avg(wpm) FROM race")
    avg = db.c.fetchone()[0]
    if not avg:
        avg = 0
    for key, stat in races.items():
        print(f'{key}: {stat}')
    print(f'Avarage: {avg:6.2f} wpm, total')

def show_current_sats(db: DataBase, intervall: int):
    """Shows stats for the last time intervall(seconds)."""
    now = datetime.now().timestamp()
    prev = int(now - intervall)
    db.c.execute("SELECT avg(wpm) FROM race WHERE timestamp >= ?", (prev,))
    last_wpm_avg = db.c.fetchone()[0]
    if not last_wpm_avg:
        last_wpm_avg = 0
    minutes = intervall // 60
    seconds = str(intervall - (minutes*60))
    seconds = seconds.zfill(2)
    print(f'Avarage: {last_wpm_avg:6.2f} wpm, last {minutes}:{seconds} minutes.')

def run():
    """Main loop for typeracer.
    
    Creates DataBase connection, Browser and runs it."""
    db = DataBase()
    db.count_words()
    racer = TypeRacer()
    racer.navigate('https://play.typeracer.com/')
    user = db.get_user()
    racer.sign_in(user)
    show_stats(db)
    while True:
        try:
            racer.wait_for_start()
            stats = racer.read_stats_loop()
            db.insert(**stats)
            show_current_sats(db, 60*10+64)
        except NoSuchElementException:
            sleep(5)
            # print('Waiting time exceeded, restarting process')
            continue
        # except NoSuchWindowException:
        #     print('lost window, closing DB connection')
        #     db.conn.close()
        #     break
        # except WebDriverException:
        #     print('Browser closed, closing DB connection')
        #     db.conn.close()
        #     break
    print('Outer loop')

if __name__ == "__main__":
    run()