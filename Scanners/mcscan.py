import threading
from bs4 import BeautifulSoup as bs
import dryscrape
import requests
import pickle
import os
import DB
import datetime


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner():
    def __init__(self):
        self.tpattern = None
        self.ipp = None
        self.company = 'MC'
        self.num = None
        self.curl = ''
        self.count = 0
        self.db = "./data/bookofjob.db"
        self.ebot = DB.DBM(self.db, self)
        self.url = "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers/fs/searchPagination/318c8bb6f553100021d223d9780d30be/%s?clientRequestID=a5410ae0479e4800ab5bdd0e14f13715"
        self.vp = "https://mastercard.wd1.myworkdayjobs.com%s"
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()


    def initialize(self):
        os.system('clear')
        print('Starting MC scan')
        headers = {'User-Agent': 'Mozilla/5.0',
                   'Connection': 'keep-alive',
                   'Accept': 'application/json, application/xml',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Referer': 'https://mastercard.wd1.myworkdayjobs.com/CorporateCareers',
                   'Accept-Encoding': 'gzip, deflate, sdch, br',
                   'Accept-Language': 'en-US',
                   'Cookie': 'wday_vps_cookie=3357977098.53810.0000, sessionLoggingInfo=1, PLAY_LANG=en-US, PLAY_SESSION=a9c56ae00488259883f54039ce3ee2b04c68ddac-mastercard_pSessionId=vgjbg5gjgt6aveqlaqvrdljap7&instance=wd1prvps0002a, timezoneOffset=300, WorkdayLB_VPS=3357977098.53810.0000'}
        session = requests.Session()
        status = 200
        results = []
        c = 0
        while True:
            result = session.get(self.url % c, headers=headers)
            try:
                result.json()[
                    'body']['children'][0]['children'][0]['listItems']
            except:
                break
            c += 50
            print('Found %s results' % c, end='\r')
            results += result.json()['body']['children'][0]['children'][0]['listItems']
        titles = [r['title']['instances'][0]['text'] for r in results]
        urls = [r['title']['commandLink'] for r in results]
        lidlist = [[i['instances'][0]['text']
                    for i in r['subtitles']] for r in results]
        self.dict = {}
        for r in range(len(results)):
            with DB.DB(self.ebot, '/data/bookofjob.db'):
                if [x for x in self.ebot._IDknown() if lidlist[r][1] in x]:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' + lidlist[r][1])
                    continue
            if self.company + ' ' + lidlist[r][1] in self.ebot.knownids:
                with DB.DB(self.ebot, self.db):
                    self.ebot.uptime(self.company + ' ' + lidlist[r][1])
                continue
            # Setting up dictionary for input
            ID = self.company + ' ' + lidlist[r][1]
            self.dict[ID] = {"Job ID": ID,
                             "Title": titles[r],
                             "Company": self.company,
                             "URL": self.vp % urls[r],
                             "Posting date": self.dsan(lidlist[r][2]),
                             "Location": lidlist[r][0]
                             }
            resp = session.get(
                self.dict[ID]['URL'] + '?clientRequestID=f21497f187294896bf593961820681ad', headers=headers)
            assert resp.status_code == 200
            try:
                resp = resp.json()[
                    'body']['children'][1]['children'][0]['children'][2]['text']
                self.dict[ID]["Catagory"] = 'None'
                a = self.htmlsplitter(resp)
                self.dict[ID]["Description"] = a
            except KeyError as ex:
                self.dict[ID]["Description"] = 'Locked'
            self.dict[ID]["Basic Skills"] = 'None'
            self.dict[ID]["Pref Skills"] = 'None'
            self.ebot.update(self.dict)
            self.dict = dict()
            print('%s out of %s done %s%% complete'%(r,len(results), (r/len(results))*100), end='\r')
        with DB.DB(self.ebot, self.db):
            self.ebot.knownids = self.ebot._IDknown()

    def dsan(self, s):
        parsed_s = [s.split()[1:3]]
        try:
            if '+' in parsed_s[0][0]:
                parsed_s[0][0] = parsed_s[0][0][:-1]
            time_dict = dict((fmt, float(amount)) for amount, fmt in parsed_s)
            dt = datetime.timedelta(**time_dict)
        except:
            return datetime.datetime.now()
        return datetime.datetime.now() - dt

    def htmlsplitter(self, html):
        track = False
        buck = ''
        for x in html:
            if x == '<':
                track = False
            elif x == '>':
                buck += '_'
                track = True
            else:
                if track:
                    buck += x
        l = [x for x in buck.split('_') if x]
        return '\n'.join(l)


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
