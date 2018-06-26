#!/usr/bin/python3.6
import os
import damaz_scan
import threading
from bs4 import BeautifulSoup as bs
import dryscrape
import datetime
import DB
import requests
import pickle

class Scanner():
    def __init__(self):
        self.tpattern = '%Y-%m-%d %H:%M:%S'
        self.ipp = 20
        self.company = 'Linkedin'
        self.kws = None
        self.num = {'name': 'span', 'id': 'showing_jobs'}
        self.curl = ''
        self.kw = pickle.load(open('Scanners/keywords', 'rb'))
        self.count = 0
        self.dict = {}
        self.url = "https://www.linkedin.com/jobs/searchRefresh?refreshType=fullpage&keywords=Linkedin&locationId=us:0&start=0&count=25&applyLogin=false&trk=jobs_jserp_pagination_1"
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

    def checky(self, check):
        if 'LinkedIn' == check['decoratedJobPosting']['jobPosting']['companyName']:
            return True
        else:
            return False

    def initialize(self):
        os.system('clear')
        print('Starting %s scan'%self.company)
        headers = {'Host': 'www.linkedin.com',
                    'Connection': 'keep-alive',
                    'Accept': '*/*',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
                    'Referer': 'https://www.linkedin.com/',
                    'Accept-Encoding': 'gzip, deflate, sdch, br',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Cookie': 'bcookie="v=2&1738815b-7bd9-4ad6-8d02-b54f3d400c8d"; bscookie="v=1&20180313182140627b023e-1264-4b14-8f73-c3cd0c7012d6AQEY27JWXk5AFLZxIOSCoNb4MqMSxSCY"; JSESSIONID=ajax:2083746939337112326; visit="v=1&G"; lidc="b=OGST03:g=635:u=1:i=1521484314:t=1521570714:s=AQHY_UVg66NByijIiL-oT4-qAoLMNPNl"; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-1891778711%7CMCIDTS%7C17610%7CMCMID%7C40336391968738964443095050040462915712%7CMCAAMLH-1522089284%7C7%7CMCAAMB-1522089284%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1521491684s%7CNONE%7CMCSYNCSOP%7C411-17617%7CvVersion%7C2.4.0; _gat=1; RT=s=1521485622326&r=https%3A%2F%2Fwww.linkedin.com%2Fjobs%2Fdirectory%2F; _ga=GA1.2.152929307.1520966845; leo_auth_token="GST:UD1ajspjW6HOBuhSON5WhcWqLGWavV-SStaWuBh3uwHSBBpG_ORblY:1521486055:25295618fba8a76d50d87afb6e0ea4052c593b4a"; lang="v=2&lang=en-us"'}
        data = {'refreshType':'fullpage',
                'keywords':'Linkedin',
                'locationId':'us:0',
                'start':'0',
                'count':'25',
                'applyLogin':'false',
                'trk':'jobs_jserp_pagination_1'}
        session = requests.Session()
        result = session.get(self.url, headers=headers, data=data)
        if result.status_code != 200:
            print('Did not get response from page')
            print('try again later or troubleshoot')
            exit()
        results = result.json()
        total = len(results['decoratedJobPostingsModule']['elements'])
        c = 0
        for result in results['decoratedJobPostingsModule']['elements']:
            if not self.checky(result):
                c += 1
                continue
            jobinfo = result['decoratedJobPosting']['jobPosting']
            with DB.DB(self.ebot, '/data/bookofjob.db'):
                if [x for x in self.ebot._IDknown() if str(jobinfo['id']) in x]:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' +
                                         str(jobinfo['id']))
                    c += 1
                    continue
            if self.company + ' ' + str(jobinfo['id']) in self.ebot.knownids:
                with DB.DB(self.ebot, self.db):
                    self.ebot.uptime(self.company + ' ' + str(jobinfo['id']))
                c += 1
                continue 
            #print("Working on %s out of %s" %
            #      (c, total, end='\r')
            # Setting up dictionary for input
            ID = self.company + ' ' + str(jobinfo['id'])
            tim = jobinfo['listDate']
            tit = jobinfo['title']
            url = result['viewJobCanonicalUrl']

            print(url)
            r = session.get(url)

            assert r.status_code == 200, 'Bad URL: \n %s' % (result['ref'])
            # Gotta convert it to a soup
            dets = bs(r.content,'lxml')
            print(dets)
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
