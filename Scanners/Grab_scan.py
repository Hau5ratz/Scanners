#!/usr/bin/python3.6
import threading
from bs4 import BeautifulSoup as bs
import requests
import os
import DB
import datetime
import pickle

class Scanner():
    def __init__(self):
        self.tpattern = '%Y-%m-%d %H:%M:%S'
        self.ipp = 20
        self.company = 'Grab'
        self.kws = None
        self.num = {'name': 'span', 'id': 'showing_jobs'}
        self.curl = ''
        self.kw = ['P2P',
                   'B2C',
                   'B2B',
                   'Payments',
                   'Application Development',
                   'Payments technology',
                   'Digital Payments',
                   'Online Payments',
                   'Account Payments',
                   'Customer Experience',
                   'Online Platform',
                   'Digital Platform',
                   'Automated Clearance',
                   'merchant',
                   'transaction',
                   'credit',
                   'debit',
                   'cards',
                   'card',
                   'ecommerce',
                   'ewallet',
                   'bitcoin',
                   'blockchain',
                   'monetization']
        self.count = 0
        self.dict = {}
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

    def checky(self, check):
        if check['experienceLevel']['id'] in ['executive', 'mid_senior_level', 'director']:
            return True
        else:
            return False

    def initialize(self):
        os.system('clear')
        print('Starting %s scan'%self.company)
        headers = { "Host": "grab.careers",
                    "Connection": "keep-alive",
                    "Content-Length": "17",
                    "X-NewRelic-ID": "VwACVV5aGwQFXVFbBQkA",
                    "Origin": "https://grab.careers",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": "https://grab.careers/jobs",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.8",
                    "Cookie": "_ga=GA1.2.253996145.1529505365; _gid=GA1.2.727418564.1529505365; _gat=1; _hjIncludedInSample=1"}
        data = {'action':'getJobList'}
        session = requests.Session()
        print('posting')
        result = session.post(
            'https://grab.careers/wp-admin/admin-ajax.php', headers=headers, data=data)
        if result.status_code != 200:
            print('Did not get response from page')
            print('try again later or troubleshoot')
            exit()
        results = result.json()
        print('got it')
        total = len(results['jobs'])
        c = 0
        for result in results['jobs']:
            with DB.DB(self.ebot, '/data/bookofjob.db'):
                if [x for x in self.ebot._IDknown() if result['reference'] in x]:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' +
                                         result['reference'])
                    c += 1
                    continue
            if self.company + ' ' + result['reference'] in self.ebot.knownids:
                with DB.DB(self.ebot, self.db):
                    self.ebot.uptime(self.company + ' ' + result['reference'])
                c += 1
                continue 
            print("Working on %s out of %s" %(c, total), end='\r')
            # Setting up dictionary for input
            ID = self.company + ' ' + result['reference']
            data = {"action":"getJobDetails",
                    "jobReference":result['reference']}
            r = session.post("https://grab.careers/wp-admin/admin-ajax.php", headers=headers, data=data)

            assert r.status_code == 200, 'Bad URL: \n %s' % (result['ref'])
            # Gotta convert it to a soup
            dets = r.json()['job']
            if not any([x in dets['description'] for x in self.kw]):
                c += 1
                continue
            self.dict[ID] = {"Job ID": ID,
                             "Title": result['title'],
                             "Company": self.company,
                             "URL": dets['applyUrl'],
                             "Catagory": dets['category'],
                             "Posting date": datetime.datetime.now(),
                             "Location": result['country']
                             }
            self.dict[ID]["Description"] = dets['description']
            self.dict[ID]["Basic Skills"] = 'None'
            self.dict[ID]["Pref Skills"] = 'None'
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
