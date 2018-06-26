import threading
from bs4 import BeautifulSoup as bs
import dryscrape
import requests
import os
import DB


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])

class Scanner():
    def __init__(self):
        self.tpattern = '%b %d, %Y'
        self.ipp = 20
        self.company = 'Samsung'
        self.kws = ['merchant services',
                    'samsung pay',
                    'issuers',
                    'mobile payments',
                    'card payments']
        self.num = {'name': 'span', 'id': 'showing_jobs'}
        self.curl = ''
        self.count = 0
        print(os.getcwd())
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        self.url = "https://careers.us.samsung.com/careers/svc/app/viewSearchJob"
        self.vp = "https://careers.us.samsung.com/careers/svc/app/viewJobDetail"
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

    def initialize(self):
        os.system('clear')
        print('Starting Samsung scan')
        headers = {'User-Agent': 'Mozilla/5.0'}
        session = requests.Session()
        for kw in self.kws:
            payload = {'keyword': kw,
                       'category': None,
                       'v_region': None,
                       'v_country': None,
                       'v_location': None,
                       'v_city': None,
                       'v_company': None,
                       'filtershowhide': 'true',
                       'searchViewRows': '20',
                       'mailcode': 'REC_RF-EX',
                       'reqstnNo': None,
                       'compCd': None,
                       'siteId': None,
                       'locnm': None,
                       'jobTitle': None,
                       'shareSenderEmail': None,
                       'shareSenderNm': None,
                       'friendEmail': None,
                       'method': 'post'}
            result = session.post(self.url, headers=headers, data=payload)
            if result.status_code != 200:
                print('Did not get response from page')
                print('try again later or troubleshoot')
                exit()
            soup = bs(result.content, 'lxml')
            results = soup.select('a[class="title"]')
            if len(results) == 0:
                print('No results skipping')
                continue
            print('results found')
            self.dict = {}
            locs = soup.select('span[class="location"]')
            #locs = locs[1::2]
            locs = [x for x in locs if len(x.text) >= 4]
            dates = soup.select('div[class="state"] > span')
            for result in results:
                with DB.DB(self.ebot, '/data/bookofjob.db'):
                    if [x for x in self.ebot._IDknown() if result['reqstnno'] in x]:
                        with DB.DB(self.ebot, self.db):
                            self.ebot.uptime(self.company + ' ' + result['reqstnno'])
                        continue
                if self.company + ' ' + result['reqstnno'] in self.ebot.knownids:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' + result['reqstnno'])
                    continue
                # Setting up post request
                payload = {'reqstnNo': result['reqstnno'],  # record ID
                           'siteId': result['siteid'],
                           'compCd': result['compcd'],
                           'jobTitle': result['jobtitle']}  # record title
                resp = session.post(self.vp, headers=headers, data=payload)

                # Setting up dictionary for input
                ID = 'samsung ' + result['reqstnno']
                try:
                    loca = locs[results.index(result)].text
                except:
                    loca = 'N/A'
                self.dict[ID] = {"Job ID": self.company + ' ' + result['reqstnno'],
                                 "Title": result['jobtitle'],
                                 "Company": self.company,
                                 "URL": self.url,
                                 "Posting date": dates[results.index(result)].text,
                                 "Location": loca
                                 }
                assert resp.status_code == 200, 'bad URL \n %s \n %s' % (
                    self.vp, self.payload)
                # Gotta convert it to a soup
                soup = bs(resp.content, 'lxml')
                # old location

                if resp.status_code != 200:
                    print('Did not get response from page')
                    print('try again later or troubleshoot')
                    exit()
                gcat = soup.find(attrs={'class':"type"})
                descs = soup.findAll('div', attrs={'class':"view_txt2"})
                try:
                    ind = gcat.text.index(',')
                    self.dict[ID]["Catagory"] = gcat.text[:ind]
                except:
                    self.dict[ID]["Catagory"] = 'None'
                self.dict[ID]["Description"] = descs[1].text
                self.dict[ID]["Basic Skills"] = descs[2].text
                self.dict[ID]["Pref Skills"] = 'None'
            self.ebot.update(self.dict)
            self.dict = dict()
            with DB.DB(self.ebot, self.db):
                self.ebot.knownids = self.ebot._IDknown()

if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
