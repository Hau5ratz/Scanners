import os
import damaz_scan
import threading
from bs4 import BeautifulSoup
import DB
import datetime
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def nlook(ide):
    return ide.split('/')[-2]


class Scanner(damaz_scan.Scanner):
    def __init__(self):
        damaz_scan.Scanner.__init__(self)
        self.tpattern = None
        self.ipp = None
        self.cwn = None
        self.company = 'Facebook'
        self.kws = pickle.load(open('Scanners/keywords', 'rb'))
        self.cat = None
        self.num = None
        self.curl = ''
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

        self.url = "https://www.facebook.com/careers/search/?q="
        # setup
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_driver = '/home/dc-user/drivers/chromedriver'
        self.driver = lambda: webdriver.Chrome(chrome_options=self.chrome_options, executable_path=self.chrome_driver)

    def initialize(self):
        self.page_scan()

    def page_scan(self):
        self.curl = self.url
        driver = self.driver()
        driver.get(self.curl)
        print('Page url: %s' % self.curl)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "._1dc4")))
        response = driver.page_source
        soup = BeautifulSoup(response, 'lxml')
        driver.close()
        results = soup.select('a[class="_5144"]')
        results = results[7:-1]
        c = 0
        local_ids = [nlook(lid['href']) for lid in results
                     if not nlook(lid['href']) in self.ebot.knownids]
        threads = []
        for loid in local_ids:
            if self.company + ' ' + loid in [l for l in self.ebot.knownids]:
                with DB.DB(self.ebot, self.db):
                    self.ebot.uptime(self.company + ' ' + loid)
                c += 1
                continue
            threads += [threading.Thread(name='thread handeling %s' % loid,
                                         target=self.mine,
                                         args=(loid,))]
            self.dict[loid] = {"Job ID": self.company + ' ' + str(loid),
                               "Posting date": datetime.datetime.now(),
                               "Company": self.company}
            self.ebot.knownids.append(loid)
            c += 1

            if c % 10 == 0 and c != 0:
                [imp.start() for imp in threads]
                [imp.join() for imp in threads]
                print("Scan %s out of %s Percent done %s%%" %
                      (c, len(local_ids), int((c/len(local_ids))*100)), end='\r')
                threads = []
                self.dict = {x : y for x, y in self.dict.items() if 'URL' in y.keys()}
                self.ebot.update(self.dict)
                self.dict = dict()
                with DB.DB(self.ebot, '../data/bookofjob.db'):
                    self.ebot.knownids = self.ebot._IDknown()
            

    def mine(self, ide):
        try:
            url = "https://www.facebook.com/careers/jobs/%s/"
            driver = self.driver()
            driver.get(url % ide)
            #print('Mine: %s' % (url % ide))
            ttok = '_4ycw'
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.' + ttok)))
            ltok = '_4ycx'
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.' + ltok)))
            ctok = '_4_n2'
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.' + ctok)))
            dtok = '_1n--'
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.' + dtok)))

            response = driver.page_source
            soup = BeautifulSoup(response, 'lxml')
            driver.close()

            title = soup.select('.' + ttok)
            loc = soup.select('.' + ltok)
            cat = soup.select('.' + ctok)
            desc = soup.select('.' + dtok)

            texty = [d.text for d in desc]

            self.dict[ide]["Title"] = title[0].text
            self.dict[ide]["Description"] = desc[-3].text
            self.dict[ide]["Catagory"] = cat[0].text
            self.dict[ide]["Location"] = loc[0].text
            self.dict[ide]["URL"] = url % ide
            self.dict[ide]["Basic Skills"] = desc[-2].text
            self.dict[ide]["Pref Skills"] = desc[-1].text
        except ConnectionRefusedError as ex:
            print('%s occured'%ex)
            self.mine(ide)


if __name__ == "__main__":
    app = Scanner()
    app.page_scan()
    print("Finished completely")
