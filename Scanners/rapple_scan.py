import os
import damaz_scan
import threading
from bs4 import BeautifulSoup
import datetime
import requests
import DB
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import http


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner(damaz_scan.Scanner):
    def __init__(self):
        damaz_scan.Scanner.__init__(self)
        self.tpattern = 'Posted: %b. %d, %Y'
        self.ipp = 20
        self.cwn = [3, 2, 1]
        self.company = 'Apple'
        self.kws = ['payments',
                    'imessage',
                    'credit',
                    'debit']
        string = 'ADMCL|AIS|RET|CSPSV|DES'\
            '|FINAN|HDWEG|HURES|MIS|CGINT|LEGAL|'\
            'MKTPM|AOS|MTLMF|PMN|FACLT|SALES|SFWEG'
        self.cat = string.split('|')
        self.num = {'name': 'span', 'id': 'showing_jobs'}
        self.curl = ''
        self.count = 0
        self.dict = dict()
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()
        self.url = 'https://jobs.apple.com/us/search/search-result'
        self.header = {'Host': ' jobs.apple.com', 'Connection': ' keep-alive', 'Content-Length': ' 166', 'Origin': ' https', 'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36', 'Content-type': ' application/x-www-form-urlencoded; charset=UTF-8', 'Accept': ' text/javascript, text/html, application/xml, text/xml, */*', 'X-Prototype-Version': ' 1.7', 'X-Requested-With': ' XMLHttpRequest', 'Referer': ' https', 'Accept-Encoding': ' gzip, deflate, br', 'Accept-Language': ' en-US,en;q=0.8',
                       'Cookie': ' jobs=1696a5237d6db4b6f9a93ad665e4c657; jobs=1696a5237d6db4b6f9a93ad665e4c657; JSESSIONID=8FH736Hmvx41PDR-A66NNrvK.nodeINST_NUM; s_ria=Flash%2030%7C; s_pathLength=jobs%3D1%2C; s_invisit_n2_us=35; ccl=sJh5ew1vOeDBoyDWTXYkaNmra6utm1VV5IhAbuUYgDA=; geo=US; jobs=1696a5237d6db4b6f9a93ad665e4c657; RecentJobs=%7B%22requisitions%22%3A%5B%7B%22jobReqId%22%3A%22113713981%22%2C%22jobReqType%22%3A%22REQ%22%2C%22postingTitle%22%3A%22Executive%20Admin%20to%20Vice%20President%20of%20Payments%20%26%20Commerce%22%7D%5D%7D; s_vnum_n2_us=35|1; s_cc=true; s_sq=%5B%5BB%5D%5D; s_vi=[CS]v1|2D90BBF0052CD9D0-400029A90001211B[CE]'}

    def initialize(self):
        print('Starting company scan: %s' % self.company)
        print('\n')
        self.ebot = DB.DBM("/data/bookjob.db", self)
        result = 1
        while result:
            li = [i, cat, kw]
            order = [li[i - 1] for i in self.cwn]
            cs = (self.url % tuple(order))
            r = request.get(cs)
            response = self.driver.page_source
            soup = BeautifulSoup(response, 'lxml')
            result = soup.find_all(*self.item)
            if not result:
                break
            self.process_page(i)
            i += self.ipp
            print("\rScan %s out of %s \t Current url: %s" %
                  (epo, len(self.cat) * len(self.kws), cs), end='\r')

    def page_scan(self, index):
        self.session = requests.session()
        payload = {'searchRequestJson': '{"searchString":"%s","jobType":"0","sortOrder":"","filters":{"jobFunctions":{"jobFunctionCode":["%s"]}},"pageNumber":"%s"}' % (self.kkw, self.ccat, index),
                   'clientOffset': '-300'}
        results = session.post(self.url, headers=self.headers, data=payload)
        print(results)
        exit()
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
                self.driver.get(self.curl + '&openJobId=' + ide)
                print(self.curl + '&openJobId=' + ide)
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sosumi")))
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".preline")))
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".square")))

                # Extract from frozen html in bs4
                # it's just easier that way

                response = self.driver.execute_script(
                    "return document.getElementsByTagName('html')[0].innerHTML")
                soup = BeautifulSoup(response, 'lxml')

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
            print('Exception: %s' % (ex))
            self.count += 1
            if self.count <= 5:
                self.mine(ide)
            else:
                del self.dict[self.company + ' ' + str(ide)]


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
