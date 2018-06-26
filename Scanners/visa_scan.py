import threading
from bs4 import BeautifulSoup as bs
import requests
import os
import DB
import pickle


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner():
    def __init__(self):
        self.tpattern = '%Y-%m-%d %H:%M:%S'
        self.ipp = 20
        self.company = 'Visa'
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

    def checky(self, check):
        if check['experienceLevel']['id'] in ['executive', 'mid_senior_level', 'director']:
            return True
        else:
            return False

    def initialize(self):
        os.system('clear')
        print('Starting Visa scan')
        headers = {'authority': 'usa.visa.com', # Needs to be reloaded every now and then
                   'method': 'GET',
                   'path': '/bin/jobdsdata.json',
                   'scheme': 'https',
                   'accept': '*/*',
                   'accept-encoding': 'gzip, deflate, sdch, br',
                   'accept-language': 'en-US,en;q=0.8',
                   'cache-control': 'max-age=0',
                   "cookie": "visaAnonCookie=6c0710609048000083642a5bfb010000ec360000; visaCookie=6c071060904800007f642a5b55010000c6360000; ak_bmsc=D6C8F33C64E378832E6AD83E88DA2F766010076C904800007F642A5BDCB8553B~plzfQ6MrJfk1Ol4grpUJkETtqLO8BH5kYFIygxYfILu6TGOmg8FVstF6kTp3l0QSL6yjZZYF0wtm7WF9iB2sDr/nCJDJoFovREwALXrgMcZ2xKAiLLv7D8sAnSoDXM4oDQ2UPiZzUdEkW5qrTdJV5gLT6I7QS+YbJH0UHFQchYaimNSauELTGoHEPI4PhNHkXSxabGlzS602O15vH6Cn9lgvpVBPHhSNqSkED7xuW1k7w=; lbs=!3qoQOk+hIwWNSS4STJ/6Qo9WwVXjT+FkSTRVewdhLl6vplpajNbpteNzGAwhmtCXAB+ylwFxwUB9qbRgAjhPuUYAng9ToOj95GsIDdo=; _dc_gtm_UA-8460445-1=1; _dc_gtm_UA-8460445-51=1; trwv.uid=visausainc-1529504898561-8000b34a%3A1; trwsa.sid=visausainc-1529504898562-1db9065a%3A1; _mkto_trk=id:608-RNC-047&token:_mch-visa.com-1529504898661-67350; pulse_insights_udid=68876851-985d-457b-93c2-e64fd75b7187; pi_pageview_count=1; pi_visit_track=true; pi_visit_count=1; _gat_UA-8460445-1=1; _ga=GA1.2.2051367998.1529504898; _gid=GA1.2.461746569.1529504898; _gali=paginationTop; _ga=GA1.3.2051367998.1529504898; _gid=GA1.3.461746569.1529504898; AKA_A2=A",
                   "upgrade-insecure-requests": "1",
                   "referer":"https://usa.visa.com/careers.html/",
                   "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
                   "x-requested-with":"XMLHttpRequest"}
        session = requests.Session()
        result = session.get(
            'https://usa.visa.com/bin/jobdsdata.json', headers=headers)
        if result.status_code != 200:
            print('Did not get response from page')
            print('try again later or troubleshoot')
            exit()
        results = result.json()
        total = results['totalFound']
        c = 0
        for result in results['content']:
            \
            if not self.checky(result):
                c += 1
                continue
            with DB.DB(self.ebot, '/data/bookofjob.db'):
                if [x for x in self.ebot._IDknown() if result['refNumber'] in x]:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' +
                                         result['refNumber'])
                    c += 1
                    continue
            if self.company + ' ' + result['refNumber'] in self.ebot.knownids:
                with DB.DB(self.ebot, self.db):
                    self.ebot.uptime(self.company + ' ' + result['refNumber'])
                c += 1
                continue 
            print("Working on %s out of %s" %
                  (c, len(results['content'])), end='\r')
            # Setting up dictionary for input
            ID = 'Visa ' + result['refNumber']

            r = session.get(result['ref'])
            assert r.status_code == 200, 'Bad URL: \n %s' % (result['ref'])
            # Gotta convert it to a soup
            dets = r.json()
            if not any([x in dets['jobAd']['sections']['jobDescription']['text'] for x in self.kw]):
                c += 1
                continue
            self.dict[ID] = {"Job ID": ID,
                             "Title": result['name'],
                             "Company": self.company,
                             "URL": result['ref'],
                             "Catagory": result['function']['label'],
                             "Posting date": result["releasedDate"].replace('T', ' ')[:-5],
                             "Location": result['customField'][1]['valueLabel']
                             }
            self.dict[ID]["Description"] = dets['jobAd']['sections']['jobDescription']['text']
            self.dict[ID]["Basic Skills"] = dets['jobAd']['sections']['qualifications']['text']
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
