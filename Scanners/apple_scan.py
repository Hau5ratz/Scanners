import os
import damaz_scan
import threading
from bs4 import BeautifulSoup
import datetime
import time
import DB
import pickle
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner(damaz_scan.Scanner):
    def __init__(self):
        damaz_scan.Scanner.__init__(self)
        self.tpattern = 'Posted: %b. %d, %Y'
        self.ipp = 20
        self.cwn = [3, 2, 1]
        self.company = 'Apple'
        self.kws = pickle.load(open('Scanners/keywords', 'rb'))
        string = 'ADMCL|AIS|RET|CSPSV|DES'\
            '|FINAN|HDWEG|HURES|MIS|CGINT|LEGAL|'\
            'MKTPM|AOS|MTLMF|PMN|FACLT|SALES|SFWEG'
        self.cat = string.split('|')
        self.num = None #{'name': 'span', 'id': 'showing_jobs'}
        self.curl = ''
        self.count = 0
        self.dict = dict()
        self.item = {'class' : 'searchresult'}
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()
        self.url = "https://jobs.apple.com/us/search?#function&ss=%s&t=0&so=&j=%s&pN=%s"
        # setup
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_driver = '/home/dc-user/drivers/chromedriver'
        self.driver = lambda: webdriver.Chrome(chrome_options=self.chrome_options, executable_path=self.chrome_driver)

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
        '''



    def page_scan(self, index):
        cat = 'td[class="detail"] > p[id="requisitionJobFunction-%s"]'
        self.curl = self.url % (self.kkw, self.ccat, index)
        d = self.driver()
        #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".blank")))
        d.get(self.curl)
        response = d.page_source
        d.close()
        d.quit()
        soup = BeautifulSoup(response, 'lxml')
        results = soup.select('.blank')
        c = 0
        local_ids = [nlook(lid['id']) for lid in results
                     if not self.company + nlook(lid['id']) in self.ebot.knownids]
        threads = []
        local_ids = [l for l in local_ids if l]
        for loid in local_ids:
            try:
                if self.company + ' ' + loid in self.ebot.knownids:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' + loid)
                    c += 1
                    continue
                threads += [threading.Thread(name='thread handeling %s' % loid,
                                             target=self.mine,
                                             args=(loid,))]
                self.dict[self.company + ' ' + str(loid)] = {"Job ID": self.company + ' ' + str(loid),
                                                             "Company": self.company,
                                                             "Posting date": datetime.datetime.now(),
                                                             "Catagory": soup.select_one(cat % loid).text}
                self.ebot.knownids.append(loid)
                c += 1
            except:
                continue
        self.count = 0
        [imp.start() for imp in threads]
        [imp.join() for imp in threads]


            #print(self.url % (self.kkw, self.ccat, index))

    def mine(self, ide):
        try:
            if not ide:
                del self.dict[self.company + ' ' + str(ide)]
            else:
                d = self.driver()
                d.get(self.curl + '&openJobId=' + ide)
                WebDriverWait(d, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sosumi")))
                WebDriverWait(d, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".preline")))
                WebDriverWait(d, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".square")))

                # Extract from frozen html in bs4
                # it's just easier that way

                response = d.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                soup = BeautifulSoup(response, 'lxml')
                d.close()
                d.quit()
                title = soup.select('#title-' + ide)
                sects = soup.select(".sosumi > li")
                desc = soup.select(".preline")
                qual = soup.select(".square > li")

                self.dict[self.company + ' ' + ide]["Title"] = title[0].text
                self.dict[self.company + ' ' +
                          ide]["Description"] = '\n'.join([d.text for d in desc])
                self.dict[self.company + ' ' + ide]["Location"] = sects[1].text
                self.dict[self.company + ' ' +
                          ide]["Posting date"] = sects[2].text
                self.dict[self.company + ' ' +
                          ide]["URL"] = self.curl + '&openJobId=' + ide
                self.dict[self.company + ' ' +
                          ide]["Basic Skills"] = '\n'.join([d.text for d in qual])
                self.dict[self.company + ' ' + ide]["Pref Skills"] = 'None'
        except (selenium.common.exceptions.TimeoutException) as ex:
            print('An exception was raised')
            print('Exception: %s'%(ex))
            self.count += 1
            if self.count <= 5:
                self.mine(ide)
            else:
                del self.dict[self.company + ' ' + str(ide)]


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
