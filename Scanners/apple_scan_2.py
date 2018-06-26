import os
import damaz_scan
import threading
from bs4 import BeautifulSoup
import dryscrape
import datetime
import DB

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
        self.url = "https://jobs.apple.com/us/search?#function&ss=%s&t=0&so=&j=%s&pN=%s"

    def page_scan(self, index):
        try:
            cat = 'td[class="detail"] > p[id="requisitionJobFunction-%s"]'
            driver, server = self.serve()
            self.curl = self.url % (self.kkw, self.ccat, index)
            driver.visit(self.curl)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".blank"))
            response = driver.body()
            driver.reset()
            server.kill()
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
        except dryscrape.mixins.WaitTimeoutError as ex:
            driver.reset()
            server.kill()

            #print(self.url % (self.kkw, self.ccat, index))

    def mine(self, ide):
        if not ide:
            del self.dict[self.company + ' ' + str(ide)]
        else:
            try:
                driver, server = self.serve()
                driver.visit(self.curl + '&openJobId=' + ide)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#title-' + ide))
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sosumi"))
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".preline"))
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".square"))

                # Extract from frozen html in bs4
                # it's just easier that way

                response = driver.body()
                driver.reset()
                server.kill()
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
            except dryscrape.mixins.WaitTimeoutError as ex:
                #print('Proc %s timed out trying again for connection'%ide)
                #print('restarting mine')
                self.count += 1
                if self.count <= 5:
                    self.mine(ide)
                else:
                    del self.dict[self.company + ' ' + str(ide)]


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
