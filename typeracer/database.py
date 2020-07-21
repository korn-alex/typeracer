import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import re


class DataBase:
    """ DB for managing TypeRacer stats."""
    race_keys = ['id','wpm','time','accuracy','points','quote_id','mode','rank','timestamp']
    quote_keys = ['id','rawtext']
    user_keys = ['id','pw']
    tables = {'race':race_keys,
            'quote':quote_keys,
            'user':user_keys}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database_file = Path.cwd() / 'typeracerstats.db'
        self._check_db()
        if not self.conn:
            self._connect_db(self.database_file)
        self.c.execute("SELECT max(id) FROM race")
        try:
            self.race_id = self.c.fetchone()[0] + 1
        except:
            self.race_id = 0
    
    def _check_db(self):
        """Checking if 'typeracerstats.db' exists."""
        f = Path(self.database_file).is_file()
        if not f:
            print('No database found')
            self._create_db()
        else:
            self._connect_db(self.database_file)
            problems = False
            for table, key in self.tables.items():
                r = self._verify(table, key)
                if not r:
                    problems = True
            if problems:
                self.conn.close()
                raise AttributeError('Something is missing in the database.')


    def _verify(self, table: str, table_keys: list) -> bool:
        """Verifies the DB structure to be correct.
        `table` is a table name to check its existence.
        `table_keys` is a list with key names in the table.
        Returns true if everything is correct.
        """
        missing_tables = False
        missing_keys = False
        self.c.execute(f"SELECT * FROM sqlite_master WHERE type='table' AND name='{table}'")
        if self.c.fetchone() is None:
            print(f'missing table "{table}"')
            missing_tables = True
        else:
            for tk in table_keys:
                self.c.execute(f"SELECT * FROM {table}")
                _keys = [k[0] for k in self.c.description]
                if tk not in _keys:
                    print(f'missing key "{tk}" in table "{table}"')
                    missing_keys = True
        if missing_keys or missing_tables:
            return False
        else:
            return True

    def _connect_db(self, name: str):
        self.conn = sqlite3.connect(name)
        self.c = self.conn.cursor()

    def _create_db(self):
        """Creates a fresh new 'typeracerstats.db'."""
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute(
        """CREATE TABLE race(
        id integer PRIMARY KEY,
        wpm integer,
        time integer,
        accuracy float,
        points integer,
        quote_id text,
        mode text,
        rank integer,
        timestamp integer
        );""")
        conn.commit()
        c.execute(
        """CREATE TABLE quote(
        id text PRIMARY KEY,
        rawtext text,
        FOREIGN KEY(id) REFERENCES race(quote_id)
        );""")
        # c.execute("""CREATE INDEX "quote_id" ON "quote" ("id");""")
        conn.commit()
        c.execute("""CREATE TABLE user(id blob PRIMARY KEY, pw blob);""")
        conn.commit()
        # c.execute("INSERT INTO race VALUES (?,?,?,?,?)", (0, 59, 23, 99.1, 69))
        # conn.commit()
        # c.execute("SELECT * FROM race")
        print(f'Created new database {self.database_file}')

    # def insert(self, wpm=0: int, time=0: int, accuracy=0: float, points=0: int, ):
    def insert(self, **kwargs):
        timestamp = int(datetime.now().timestamp())
        race_id = self.race_id
        quote = kwargs.get('quote')
        h = hashlib.sha1(quote.encode())
        quote_hash = h.hexdigest()
        values = [
            kwargs.get('wpm'),
            kwargs.get('time'),
            kwargs.get('accuracy'),
            kwargs.get('points'),
            quote_hash,
            kwargs.get('mode'),
            kwargs.get('rank'),
            timestamp
        ]
        
        self.c.execute("SELECT id FROM quote WHERE id==(?)", (quote_hash,))
        quote_exists = self.c.fetchone()
        if not quote_exists:
            self.c.execute("INSERT INTO quote VALUES (:id, :text)", (quote_hash, quote))
            self.conn.commit()
        self.c.execute("INSERT INTO race VALUES (:id, :wpm, :time, :accuracy, :points, :text, :mode, :rank, :timestamp)", (race_id, *values))
        self.conn.commit()
        self.race_id = self.c.lastrowid + 1

    def get_user(self):
        """Returns (user, pw)"""
        self.c.execute("SELECT * FROM user")
        try:
            u, p = self.c.fetchone()
        except ValueError:
            return None
        except TypeError:
            return None
        return (u, p)

    def count_races(self) -> dict:
        """Returns amount of races from database.
        
            `total=int`

            `race_count=int`
            
            `practice_count=int`
        """
        self.c.execute("SELECT COUNT (*) FROM race WHERE mode='race'")
        race_count = self.c.fetchone()[0]
        self.c.execute("SELECT COUNT (*) FROM race WHERE mode='practice'")
        practice_count = self.c.fetchone()[0]
        if not race_count:
            race_count = 0
        if not practice_count:
            practice_count = 0
        total = race_count + practice_count
        d = {'total':total, 'race_count':race_count, 'practice_count':practice_count}
        return d
    
    def count_words(self) -> int:
        r = re.compile(r'\S+(?=\s)')
        self.c.execute("SELECT quote_id FROM race")
        qids = self.c.fetchall()
        self.c.execute("SELECT id, rawtext FROM quote")
        quotes = self.c.fetchall()

        quotes_text = []
        for id in qids:
            for quote in quotes:
                if id[0]==quote[0]:
                    quotes_text.append(quote[1])
        wordcount = 0
        for quote in quotes_text:
            words = r.findall(quote)
            wordcount += len(words)
        return wordcount

if __name__ == "__main__":
    stats = {}
    stats['wpm'] = 3
    stats['time'] = 654
    stats['accuracy'] = 40
    stats['points'] = 39
    stats['quote'] = "weiterer täxt'"
    db = DataBase()
    # db.insert(**stats)
    db.count_words()