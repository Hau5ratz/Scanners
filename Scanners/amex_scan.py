import threading
from bs4 import BeautifulSoup as bs
import requests
import os
import DB
import pickle
import simplejson


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner():
    def __init__(self):
        self.tpattern = '%Y-%m-%dT%H:%M:%S'
        self.ipp = 20
        self.company = 'Amex'
        self.url = 'https://jobs.americanexpress.com/api/jobs?page=%s&limit=100'
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
        self.num = {'name': 'span', 'id': 'showing_jobs'}
        self.curl = ''
        self.ledger = ''
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
        print('Starting Amex scan')
        session = requests.Session()
        c = 1
        pulls = []
        while True:
            result = session.get(self.url % (c))
            if result.status_code != 200:
                print('Did not get response from page')
                print('try again later or troubleshoot')
                exit()
            results = result.json()
            if results['jobs']:
                pulls += results['jobs']
                c += 1
            else:
                break
        i, l = 1, len(pulls)        
        for pull in pulls:
            idy = self.company + ' ' + pull['data']['slug']
            with DB.DB(self.ebot, '/data/bookofjob.db'):
                if [x for x in self.ebot._IDknown() if idy in x]:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(idy)
                    i += 1
                    continue
            if idy in self.ebot.knownids:
                with DB.DB(self.ebot, self.db):
                    self.ebot.uptime(idy)
                i += 1
                continue
            print("Working on %s out of %s" %
                  (i, l), end='\r')
            if any([x in pull['data']['description'] for x in self.kw]) and pull['data']['meta_data']['schedule'] == 'Full-time':
                self.mine(pull)
            i += 1
        print(len(self.dict))
        self.ebot.update(self.dict)
        with DB.DB(self.ebot, self.db):
            self.ebot.knownids = self.ebot._IDknown()

    def mine(self, pull):
        ID = self.company + ' ' + pull['data']['slug']
        self.dict[ID] = {}
        self.dict[ID]["Job ID"] = ID
        self.dict[ID]["Title"] = pull['data']['title']
        self.dict[ID]["Company"] = self.company
        self.dict[ID]["URL"] = pull['data']['apply_url']
        self.dict[ID]["Catagory"] = pull['data']['categories'][0]['name']
        self.dict[ID]["Posting date"] = pull['data']['create_date'][:-5]
        self.dict[ID]["Description"] = pull['data']['description']
        self.dict[ID]["Location"] = pull['data']['full_location']
        self.dict[ID]["Basic Skills"] = 'None'
        self.dict[ID]["Pref Skills"] = 'None'
        if ID not in self.dict.keys():
            print('ERROR')


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
