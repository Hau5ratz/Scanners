import sqlite3
import os
import time
from geopy.geocoders import Nominatim
import sys


class DB():
    def __init__(self, owner, db):
        self.db = "./data/bookofjob.db"
        self.owner = owner

    def __enter__(self):
        if os.path.exists(self.db):
            self.owner.conn = sqlite3.connect(self.db)
            self.owner.c = self.owner.conn.cursor()
        else:
            print(self.db)
            print('database does not exist')
            exit()

    def __exit__(self, type, value, traceback):
        try:
            self.owner.conn.commit()
        except:
            pass
        self.owner.conn.close()


class DBM():
    def __init__(self, db, user):
        self.db = db
        with DB(self, self.db):
            self.knownids = self._IDknown()
            self.CATknown = self._catlearn()
            self.CUNknown = self._CCknown()
            self.COMknown = self._COknown()
            self.pattern = user.tpattern  # maybe important
            self.t = self._namet()
            self.bin1 = dict()
            self.bin2 = dict()
            self.geo = Nominatim()
            self.gon = True
            if 'NO' not in self.CUNknown:
                x = ['NO', 'No information']
                self._update('country', x)
                self.CUNknown.append('NO')

    def columns(self, table):
        '''
        Gives the column names of a give table
        '''
        insert = '''
                PRAGMA
                table_info(%s)
                ''' % table
        self.c.execute(insert)
        return [x[1] for x in self.c]

    def update(self, dc):
        c = 0 
        tots = len(dc)
        with DB(self, self.db):
            for key, value in dc.items():
                t = self.t[0]
                columns = self.columns(t)
                try:
                    values = [key, value['URL'], int(time.time())]
                except:
                    print('Huge issue with DB:')
                    print(value)
                    print(dc)
                    exit()
                try:
                    self._update(t, values)
                except:
                    print('_update:')
                    print(t, values)
                    print([v[0] for v in dc.values()])
                    exit()
                for k, v in value.items():
                    if k in ['Job ID', 'URL']:
                        continue
                    elif k == 'Location':
                        t = self.t[-2]
                        # Mac Patch
                        g = self._gsant(v)
                        if g:
                            self._update(t, [key] + g)
                        else:
                            self._update(
                                t, [key, 'NO', v, 'False', 'False', 'False'])
                        # end of mac patch
                    elif k == 'Catagory':
                        t = self.t[-3]
                        self._update(t, [key, self._csant(v)])
                    elif k == 'Posting date':
                        if v is None:
                            continue
                        else:
                            t = self.t[-1]
                            self._update(t, [key, self._tsant(v)])
                    elif k == 'Company':
                        t = self.t[3]
                        self._update(t, [key, self._corpsant(v)])

                insert = [key,
                          value["Description"],
                          value["Basic Skills"],
                          value["Pref Skills"],
                          value["Title"]]

                self._update(self.t[-5], insert)
                c += 1
                print('\t\t\tUpdating db %s/%s'%(c, tots), end='\r')

            self.knownids = self._IDknown()
            
            

    def _update(self, tname, values, e=False):
        '''
                Get's a dictionary in the format:

                {key:dick}
                dick = {columnn:columnv}
        '''
        try:
            columns = self.columns(tname)

            ######################
            # Sanatize:
            values = [v.replace("'", "") if isinstance(
                v, str) else v for v in values]
            values = [v[0] if isinstance(
                v, tuple) else v for v in values]
            values = [v if isinstance(v, int) else "'" +
                      v + "'" for v in values]
            #####################
            insert = '''INSERT INTO %s '''
            col = '(%s' + (', %s' * (len(columns) - 1)) + ')'
            val = ' VALUES (%s' + (', %s' * (len(values) - 1)) + ')'
            inject = insert % tname
            inject += col % tuple(columns)
            inject += val % tuple(values)
            self.c.execute(inject)
        except sqlite3.IntegrityError as ex:
            os.system('clear')
            print("Here's the error: %s" % ex)
            print("Assume the worst")
            exit()
        except TypeError as ex:
            print('Encountered %s' % (ex))
            print(tname)
            print(values)
            exit()

    def pull(self, tname, values, e=False):
        with DB(self, self.db):
            columns = self.columns(tname)
            ######################
            # Sanatize:
            values = [v.replace("'", "") if isinstance(
                v, str) else v for v in values]
            values = [v if isinstance(v, int) else "'" +
                      v + "'" for v in values]
            #####################
            insert = '''SELECT FROM %s '''
            col = '(%s' + (', %s' * (len(columns) - 1)) + ')'
            val = ' VALUES (%s' + (', %s' * (len(values) - 1)) + ')'
            inject = insert % tname
            inject += col % tuple(columns)
            inject += val % tuple(values)
            self.c.execute(inject)

    # Sanatizers

    def _gsant(self, v):
        '''
        Geography Sanatizer
        '''
        try:
            loc = self.geo.geocode(v, addressdetails=True)
            d = loc.raw
            ad = d['address']
            if ad['country_code'] not in self.CUNknown:
                x = [ad['country_code'], ad['country']]
                y = self.columns('country')
                self._update('country', x)
                self.CUNknown.append(ad['country_code'])
            pack = []
            it = ['country_code', 'state', 'state_district',
                  'county', 'town', 'type']
            pause = True
            for x in it:
                try:
                    if pause and x == 'state_district':
                        continue
                    pack.append(ad[x])
                except KeyError:
                    if x == 'state':
                        pause = False
                        continue
                    pack.append('None')
            return pack
        except Exception as ex:
            return False

    def _corpsant(self, v):
        if v not in self.COMknown.keys():
            if self.COMknown.values():
                n = max(self.COMknown.values()) + 1
            else:
                n = 1
            self._update(self.t[2], [n, v])
            self.COMknown = self._COknown()
            self.bin2[v] = n
            self.COMknown = dict(self.bin2, **self.COMknown)
        return self.COMknown[v]

    def uptime(self, v):
        update = '''UPDATE active_jobs '''
        col = 'SET last_update = %s'
        val = ' WHERE ID = %s'
        inject = update
        inject += col % int(time.time())
        inject += val % ("'" + v + "'")
        self.c.execute(inject)

    def _csant(self, v):
        '''
        Catagory Sanatizer
        '''
        self.CATknown = self._catlearn()
        if v not in self.CATknown.keys():
            if self.CATknown.values():
                n = max(self.CATknown.values()) + 1
            else:
                n = 1
            self._update(self.t[1], [n, v])
            self.CATknown = self._catlearn()
            self.bin1[v] = n
            self.CATknown = dict(self.bin1, **self.CATknown)
        return self.CATknown[v]

    def _tsant(self, v):
        if isinstance(v, str):
            return int(time.mktime(time.strptime(v, self.pattern)))
        else:
            return int(v.timestamp())

    # Data pullers

    def _IDknown(self):
        insert = '''
                SELECT ID
                FROM active_jobs
                '''
        self.c.execute(insert)
        return [x[0] for x in self.c]

    def _CCknown(self):
        insert = '''
                SELECT country_code
                FROM country
                '''
        self.c.execute(insert)
        return [x[0] for x in self.c]

    def _COknown(self):
        insert = '''
                SELECT comp_ID, name
                FROM companies
                '''
        self.c.execute(insert)
        return {x[1]: x[0] for x in self.c}

    def _namet(self):
        insert = '''
                SELECT name
                FROM sqlite_master
                WHERE type="table"
                '''
        self.c.execute(insert)
        return [x[0] for x in self.c]

    def _catlearn(self):
        insert = '''
                SELECT cat_id, name
                FROM categories
                '''
        self.c.execute(insert)
        return {x[1]: x[0] for x in self.c}

    # Extranious

    def _exit(self):
        self.conn.close()
        sys.exit(0)
