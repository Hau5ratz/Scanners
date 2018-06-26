import threading
from bs4 import BeautifulSoup as bs
import requests
import os
import DB
import pickle
import simplejson
import datetime


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner():
    def __init__(self):
        self.tpattern = "%m/%d/%Y"
        self.ipp = 20
        self.company = 'paypal'
        self.url = 'https://jobsearch.paypal-corp.com/en-US/search?Scanners/keywords=%s&pagenumber=%s'
        self.kw = pickle.load(open('Scanners/keywords', 'rb'))
        self.curl = 'https://jobsearch.paypal-corp.com'
        self.ledger = set()
        self.count = 0
        self.dict = {}
        self.db = "./data/bookofjob.db"
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

    def initialize(self):
        os.system('clear')
        print('Starting Paypal scan')
        self.session = requests.session()
        c = 1
        for kkw in self.kw:
            self.kkw = kkw
            result = self.session.get(self.url % (kkw, 1))
            if result.status_code != 200:
                print('Did not get response from page: ' + self.url % (kkw, 1))
                print('try again later or troubleshoot')
                exit()
            soup = bs(result.content, 'lxml')
            num = soup.findAll(attrs={'class': "jrp-pagination-number"})
            try:
                its = max([int(n.text) for n in num])
            except:
                its = None
            self.pagescan(soup)
            if its:
                for x in range(2, its):
                    result = self.session.get(self.url % (kkw, x))
                    if result.status_code != 200:
                        print('Did not get response from page: ' +
                              self.url % (kkw, x))
                        print('try again later or troubleshoot')
                        exit()
                    self.pagescan(bs(result.content, 'lxml'))

    def pagescan(self, soup):
        hits = soup.findAll(attrs={'class': "job-result-title"})
        pulls = [n['href'] for n in hits]
        self.i = 1
        for pull in pulls:
            print("Working on %s out of %s for cat %s/%s" %
                  (self.i, len(pulls), self.kw.index(self.kkw), len(self.kw)), end='\r')
            self.mine(pull)
            self.i += 1
        self.ebot.update(self.dict)
        self.dict = {}
        with DB.DB(self.ebot, self.db):
            self.ebot.knownids = self.ebot._IDknown()

    def mine(self, pull):
        result = self.session.get(self.curl + pull)
        if result.status_code != 200:
            print('Did not get response from page: ' +
                  self.curl + pull)
            print('try again later or troubleshoot')
            exit()
        soup = bs(result.content, 'lxml')
        try:
            ID = self.company + ' ' + soup.findAll('div' , attrs={'class': "secondary-text-color"})[-1].text
        except IndexError as ex:
            return
        if ID in self.ebot.knownids:
            with DB.DB(self.ebot, self.db):
                self.ebot.uptime(ID)
            return False
        self.dict[ID] = {}
        self.dict[ID]["Job ID"] = ID
        self.dict[ID]["Title"] = soup.findAll(
            attrs={'class': "jdp-job-title"})[0].text.replace('  ', '')
        self.dict[ID]["Company"] = self.company
        self.dict[ID]["URL"] = self.curl + pull
        self.dict[ID]["Catagory"] = soup.findAll(
            attrs={'class': "job-snapshot-link"})[1].text
        date = soup.findAll(
            attrs={'class': "job-date-posted"})[0].text[14:-1].split('/')
        month = '0' + date[0] if len(date[0]) == 1 else date[0]
        day = '0' + date[1] if len(date[1]) == 1 else date[1]
        self.dict[ID]["Posting date"] = '/'.join([month, day, date[2]])
        self.dict[ID]["Description"] = soup.findAll(
            attrs={'class': "jdp-job-description-card"})[0].text
        self.dict[ID]["Location"] = soup.findAll(
            attrs={'class': "jobLocation"})[0].text
        self.dict[ID]["Basic Skills"] = 'None'
        self.dict[ID]["Pref Skills"] = 'None'
        if ID not in self.dict.keys():
            print('ERROR')


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
