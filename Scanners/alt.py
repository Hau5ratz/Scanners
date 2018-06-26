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
        self.kws = None
        self.num = {'name': 'span', 'id': 'showing_jobs'}
        self.curl = ''
        self.ledger = ''
        self.count = 0
        self.dict = {}
        print(os.getcwd())
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
        result = session.get(self.url % (1))
        if result.status_code != 200:
            print('Did not get response from page')
            print('try again later or troubleshoot')
            exit()
        results = result.json()
        total = results['totalCount']
        self.c = 0
        print('starting first mine')
        self.mine(results)
        print('first mine done\n')
        for i in range(2, int(total / 100) + 1):
            try:
                result = session.get(self.url % (i))
                result = result.json()
            except simplejson.errors.JSONDecodeError as j:
                print(j)
                result = session.get(self.url % (i))
                result = result.json()
            self.mine(result)
        print('uploading length of upload: %s' % len(self.dict))
        self.ebot.update(self.dict)
        with DB.DB(self.ebot, self.db):
            self.ebot.knownids = self.ebot._IDknown()

    def mine(self, results):
        for result in results['jobs']:
            #print("Working on %s out of %s" %
            #      (self.c, results['totalCount']), end='\r')
            print(len(self.dict))
            with DB.DB(self.ebot, '/data/bookofjob.db'):
                if [x for x in self.ebot._IDknown() if result['data']['slug'] in x]:
                    self.c += 1
                    continue
            if self.company + ' ' + result['data']['slug'] in self.ebot.knownids:
                #print("skipping ID: %s" % result)
                self.c += 1
                continue
            # Setting up dictionary for input
            ID = self.company + ' ' + result['data']['slug']
            self.dict[ID] = {"Job ID": ID,
                             "Title": result['data']['title'],
                             "Company": self.company,
                             "URL": result['data']['apply_url'],
                             "Catagory": result['data']['categories'][0]['name'],
                             "Posting date": result['data']['create_date'][:-5],
                             "Description": result['data']['description'],
                             "Location": result['data']['full_location']
                             }
            self.dict[ID]["Basic Skills"] = 'None'
            self.dict[ID]["Pref Skills"] = 'None'
            if ID not in self.dict.values():
                print('ERROR')
            self.c += 1


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
