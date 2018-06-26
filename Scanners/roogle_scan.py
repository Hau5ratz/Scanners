from __future__ import print_function
import damaz_scan
import threading
from bs4 import BeautifulSoup
import pickle
import os
import time

def pull(url):
    os.system('python2 get.py %s'%url)
    while True:
        if os.path.isfile('check.txt'):
            with open('html', 'rb') as file:
                p = pickle.load(file)
            os.system('rm html')
            return p
'''
Need to rewrite template to handel None reported results

'''


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner(damaz_scan.Scanner):
    def __init__(self):
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()
        damaz_scan.Scanner.__init__(self)
        self.tpattern = None
        self.ipp = 20  # This is the posts per page
        self.cwn = [1, 3, 2]
        self.company = 'Google'
        self.kws = ['payments',
                    'andriod pay',
                    'merchant',
                    'google exspress',
                    'AML']

        self.cat = ['BUSINESS_STRATEGY', 'DATA_CENTER_OPERATIONS',
                    'DEVELOPER_RELATIONS', 'ADMINISTRATIVE',
                    'FINANCE', 'HARDWARE_ENGINEERING',
                    'INFORMATION_TECHNOLOGY', 'LEGAL',
                    'MANUFACTURING_SUPPLY_CHAIN', 'MARKETING',
                    'NETWORK_ENGINEERING', 'PARTNERSHIPS',
                    'PEOPLEOPS', 'PRODUCT_SUPPORT',
                    'PRODUCT_MANAGEMENT', 'PROGRAM_MANAGEMENT',
                    'REAL_ESTATE', 'SALES', 'SALES_OPERATIONS',
                    'GOOGLEORG', 'SOFTWARE_ENGINEERING',
                    'TECHNICAL_INFRASTRUCTURE_ENGINEERING',
                    'TECHNICAL_SOLUTIONS', 'TECHNICAL_WRITING',
                    'USER_EXPERIENCE']
        self.num = None
        self.indic = ('div[tabindex=-1]')
        self.curl = ''
        self.item = ('div', "sr-content-text")

        self.url = "https://careers.google.com/jobs#t=sq&q=j&li=20&st=%s&l=false&jlo=en-US&j=%s&jc=%s&"

    def page_scan(self, index):
        # try:
        print('starting page scan')
        self.curl = self.url % (index, self.kkw, self.ccat)
        x = pull(self.curl)
        #print('Page url: %s' % self.curl)
        response = x
        soup = BeautifulSoup(response, 'lxml')
        results = soup.select(self.indic)
        c = 0
        local_ids = [nlook(lid['id']) for lid in results
                     if not nlook(lid['id']) in self.ebot.knownids]
        threads = []
        for loid in local_ids:
            if self.company + ' ' + loid in self.ebot.knownids:
                self.ebot.uptime(self.company + ' ' + loid)
                c += 1
                continue
            threads += [threading.Thread(name='thread handeling %s' % loid,
                                         target=self.mine,
                                         args=(loid,))]
            self.dict[self.company + ' ' + str(loid)] = {"Job ID": self.company + ' ' + str(loid),
                                                         "Company": self.company,
                                                         "Catagory": self.ccat}
            self.ebot.knownids.append(loid)
            c += 1

        [imp.start() for imp in threads]
        [imp.join() for imp in threads]
        # except dryscrape.mixins.WaitTimeoutError as ex:
        #print('an error has occured')
        #print('The error is %s'%ex)
        # driver.reset()
        # server.kill()
        #
        #print(self.url % (self.kkw, self.ccat, index))

    def mine(self, ide):
        try:
            response = pull("https://careers.google.com/jobs#!t=jo&jid=" + ide)
            # print('Mine: %s' % ("https://careers.google.com/jobs#!t=jo&jid=" + ide))
            #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sosumi"))
            #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".preline"))
            #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".square"))

            # Extract from frozen html in bs4
            # it's just easier that way
            soup = BeautifulSoup(response, 'lxml')

            title = soup.select('a.title.text')
            loc = soup.select("a.details-location")
            desc = soup.select("div.with-benefits p")
            stuff = soup.find_all("div", class_="details-panel")
            qual = soup.select('div.GXRRIBB-S-c')
            pref = qual[1].select("li")
            qual = qual[0].select("li")
            self.dict[self.company+' '+ str(ide)]["Title"] = title[0].text
            self.dict[self.company +
                      ide]["Description"] = '\n'.join([d.text for d in desc])
            self.dict[self.company+' '+ str(ide)]["Location"] = loc[0].text
            self.dict[self.company+' '+ str(ide)]["Posting date"] = None
            self.dict[self.company +
                      ide]["URL"] = "https://careers.google.com/jobs#!t=jo&jid=" + ide
            self.dict[self.company +
                      ide]["Basic Skills"] = '\n'.join([d.text for d in qual])
            self.dict[self.company +
                      ide]["Pref Skills"] = '\n'.join([d.text for d in qual])
        except:
            print('Proc %s timed out trying again for connection' % ide)
            print('restarting mine')
            self.mine(ide)


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
