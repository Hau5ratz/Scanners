import os
import requests
from bs4 import BeautifulSoup
import sqlite3
import DB
import datetime
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Scanner():
    def __init__(self):
        os.system('clear')
        self.cwn = [1, 2, 3]
        self.tpattern = 'whaat. %B'
        self.company, self.ccat, self.kkw = "", "", ""
        self.url, self.num, self.jobs = "", "", ""
        self.kws, self.cat = [], []
        self.dict = dict()
        self.months = [datetime.date(2000, m, 1).strftime('%B')
                       for m in range(1, 13)]
        self.ebot = DB.DBM("../data/bookofjob.db", self)
        # setup
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_driver = '/home/dc-user/drivers/chromedriver'
        self.driver = lambda : webdriver.Chrome(chrome_options=self.chrome_options, executable_path=self.chrome_driver)
        # Establish OS systems


    def process_page(self, i):
        t = time.time()
        self.page_scan(i)
        self.mem = int((time.time() - t))
        self.ebot.update(self.dict)
        self.dict = dict()
        with DB.DB(self.ebot, '/data/bookjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

    '''
    def tprocess_page(self, i):
        self.threads += [threading.Thread(target=self.page_scan,
                                                 name="Thread scanning index - %s" % str(
                                                     i),
                                                 args=(i,))]
        print('before if')
        if len(self.threads) >= self.c:
            self.sustain = False
        else:
            print('in else')
            t = time.time()
            [imp.start() for imp in self.threads]
            [imp.join() for imp in self.threads]

            self.left -= len(self.threads)
            if time.time() - t < self.mem * self.c * 1.5:
                self.c += 1
            else:
                if self.c > 1:
                    self.c -= 1
            self.mem = int((time.time() - t) / self.c)

            out = 'thread finished taking %s seconds' % (str(len(self.threads)), int(self.mem))
            x = (int(self.reps) - self.left, int(self.reps), int((int(self.reps) - self.left) / int(self.reps) * 100))
            print(out + ' %s out of %s left %s done' % x, end='\r')

            if not all(['URL' in self.dict[v] for v in self.dict.keys()]):
                print("Error Caught")
                v = [v for v in self.dict.keys() if not 'URL' in self.dict[v]]
                print(v)
                self.dict[v[0]] = '%s&openJobId=%s'%(self.curl, v[0])

            with Server():
                self.ebot.update(self.dict)
                
                self.dict = dict()
                with DB.DB(self.ebot,'/data/bookjob.db'):
                    self.ebot.knownids = self.ebot._IDknown()
                self.threads, self.sustain = [], True
    '''

    def initialize(self):
        print('Starting company scan: %s' % self.company)
        print('\n')
        self.ebot = DB.DBM("/data/bookjob.db", self)
        epo = 0
        for kw in self.kws:
            self.kkw = kw
            for cat in self.cat:
                epo += 1
                self.ccat = cat
                self.threads, self.c = [], 1
                self.sustain, self.mem = True, 360
                li = [0, cat, kw]
                order = [li[i - 1] for i in self.cwn]
                text = ''
                cs = (self.url % tuple(order))
                response = requests.get(cs)
                self.c = 1
                soup = BeautifulSoup(response.content, 'lxml')
                if self.num:  # Numbered version
                    print("Scan %s out of %s \t Current url: %s" %
                          (epo, len(self.cat) * len(self.kws), cs), end='\r')
                    text = soup.find(**self.num)
                    # print('URL: %s'%cs)
                    if not text:
                        continue
                    text = text.text
                    try:
                        num = max([x for x in text.split() if x.isdigit()])
                    except ValueError:
                        print('\n')
                        print('No max number ERROR')
                        print(self.url % tuple(order))
                        print(text)
                        print([x for x in text if x.isdigit()])
                        continue
                    self.reps = int(int(num) / self.ipp)
                    if self.reps == 0:
                        self.reps += 1
                    self.left = self.reps
                    for i in range(self.reps):
                        self.process_page(i)
                else:  # Numberless version
                    self.rep = None
                    result = True
                    i = 0
                    while result:
                        li = [i, cat, kw]
                        order = [li[i - 1] for i in self.cwn]
                        cs = (self.url % tuple(order))
                        d = self.driver()
                        d.get(cs)
                        try:
                            d.WebDriverWait(d, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "." + self.item[1])))
                        except:
                            pass
                        response = d.page_source
                        soup = BeautifulSoup(response, 'lxml')
                        result = soup.find_all(*self.item)
                        if not result:
                            break
                        self.process_page(i)
                        i += self.ipp
                        d.exit()
                    print("\rScan %s out of %s \t Current url: %s" %
                          (epo, len(self.cat) * len(self.kws), cs), end='\r')

        # self.driver.close()
        print("Done")
