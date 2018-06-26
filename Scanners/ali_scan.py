import threading
from bs4 import BeautifulSoup as bs
import requests
import os
import DB
import pickle
import time
import datetime


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner():
    def __init__(self):
        self.tpattern = ''
        self.ipp = 20
        self.company = 'Alibaba'
        self.kws = None
        self.num = {'name': 'span', 'id': 'showing_jobs'}
        self.curl = ''
        self.kw = pickle.load(open('Scanners/keywords', 'rb'))
        self.count = 0
        self.dict = {}
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

    def initialize(self):
        os.system('clear')
        print('Starting %s scan' % self.company)
        for kw in self.kw:
            headers = {'authority': 'careers.alibaba.com',
                       'method': 'GET',
                       'path': '/socialPositionList.json?_api=getPositionList&_mock=false&categorys=&keyword=&location=&pageIndex=1&pageSize=10&_stamp=%s' % time.time(),
                       'scheme': 'https',
                       'accept': 'application/json, text/json',
                       'accept-encoding': 'gzip, deflate, sdch, br',
                       'accept-language': 'en-US,en;q=0.8',
                       'cache-control': 'max-age=0',
                       "cookie": "cna=6QovE+xA+iMCAdh31cH0F6Xx; isg=BH9_AlSpGR7Alx0CHY305nKqDlWldGc4TA7TDRFPci_bIJ6iGzR2V89xZujeOat-",
                       "upgrade-insecure-requests": "1",
                       "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"}
            session = requests.Session()
            result = session.get(
                'https://careers.alibaba.com/socialPositionList.json?_api=getPositionList&_mock=false&categorys=&keyword=%s&location=&pageIndex=1&pageSize=1000&_stamp=%s' % (kw, time.time()), headers=headers)
            if result.status_code != 200:
                print('Did not get response from page')
                print('try again later or troubleshoot')
                exit()
            results = result.json()
            c = 0
            l = len(results['content']["datas"])
            for result in results['content']["datas"]:
                ID = result['id']
                if ID in self.ebot.knownids:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(ID)
                    c += 1
                    continue
                print("Working on %s out of %s" %(c, l), end='\r')

                self.dict[ID] = {"Job ID": ID,
                                 "Title": result['name'],
                                 "Company": self.company,
                                 "URL": 'None',
                                 "Catagory": result['categoryEnName'],
                                 "Location": result['workLocation']
                                 }
                try:
                    self.dict[ID]["Posting date"] = datetime.datetime.fromtimestamp(int(str(result["gmtCreate"])[:-3]))
                except Exception as ex:
                    print(ex)
                    print(result["gmtCreate"])
                    exit()
                self.dict[ID]["Description"] = result['description']
                self.dict[ID]["Basic Skills"] = result['degree']
                self.dict[ID]["Pref Skills"] = result['workExperience']

                c += 1
                print()
                print('pushing to database...')
                print(len(self.dict))
        self.ebot.update(self.dict)
        print('database updated')
        self.dict = dict()
        with DB.DB(self.ebot, self.db):
            self.ebot.knownids = self.ebot._IDknown()


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
