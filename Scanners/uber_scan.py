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
        self.tpattern = '%Y-%m-%d %H:%M %p'
        self.ipp = 20
        self.company = 'Uber'
        self.kws = None
        self.num = {'name': 'span', 'id': 'showing_jobs'}
        self.sapi = 'https://www.uber.com/api/jobs/filter?country=all&city=all&team=all&subTeam=all&keywords=%s&page=1000'
        self.japi = 'https://www.uber.com/api/jobs/'
        self.kw = pickle.load(open('Scanners/keywords', 'rb'))
        self.cookies = '''uber-com:sess=O6D7TqaARWdRVBEZGqQvvA.bg7rJQfDMhhpYR8AZcfDuTjzdvSr6wFsPK4dWd28Z5bTZf5dT5FggtTUjkt_dbOx8Vmj9d1XLFqNpUlKvW936IVE3VW3fhApnuNcHkCBfi3dVv8ZrWWbDnllT6UnHujE6u2ju4k5TmbVPH16iQkFopQHMbiYFzy2jPKl0-KlikSytnGy65cr4R9j_kXXWzB2.1520973288433.1209600000.oG0x8HMw1Y9KdZSyY5QWMHgG4LhHl_Z-esSEaZykJl8;
                         AMCVS_0FEC8C3E55DB4B027F000101%40AdobeOrg=1;
                         AAMC_uber_0=AMSYNCSOP%7C411-17611;
                         AMCV_0FEC8C3E55DB4B027F000101%40AdobeOrg=1611084164%7CMCMID%7C40006176189925084563065968796371822420%7CMCAAMLH-1521578091%7C7%7CMCAAMB-1521637204%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1521039604s%7CNONE%7CMCSYNCSOP%7C411-17611;
                         optimizelyEndUserId=oeu1520973289372r0.2671368253176445;
                         _ga=GA1.2.1004332836.1520973292;
                         _gid=GA1.2.868717410.1520973292;
                         QSI_HistorySession=https%3A%2F%2Fwww.uber.com%2Fcareers%2Flist%2F%3Fcity%3Dall%26country%3Dall%26keywords%3D%26subteam%3Dall%26team%3Dall~1521032665920;
                         utag_main=v_id:016221129e230021cb38b5b1d45004078001d07000bd0$_sn:3$_ss:0$_st:1521035205620$segment:a$optimizely_segment:a$ses_id:1521032403904%3Bexp-session$_pn:5%3Bexp-session;
                         aam_uuid=39782114941332526633043585219621505867;
                         rx_jobid=31339;
                         _RCRTX03=fec143d026fd11e89e0d39ab34b4a0dcd38bf0d87dc643958f6cd4aae703c9ce;
                         marketing_vistor_id=4d2af233-c998-4e62-97b7-57362a36c3ec'''.replace('\n', '')
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
        print('Starting Uber scan')
        for kw in self.kw:
            headers = {'accept': 'ext/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'accept-encoding': 'gzip, deflate, sdch, br',
                       'accept-language': 'en-US,en;q=0.8',
                       'cache-control': 'max-age=0',
                       'Connection': 'keep-alive',
                       'Upgrade-Insecure-Requests': '1',
                       "cookie": self.cookies,
                       "If-None-Match": 'W/"5d12c-DU4REOm0sOBBfI9F3wFlAW0juD0"',
                       "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"}
            session = requests.Session()
            result = session.get(self.sapi%(kw), headers=headers)
            if result.status_code != 200:
                print('Did not get response from page')
                print('try again later or troubleshoot')
                exit()
            results = result.json()
            total = len(results['jobs'])
            c = 0
            for result in results['jobs']:
                ID = self.company + ' ' + result['id']
                with DB.DB(self.ebot, '/data/bookofjob.db'):
                    if [x for x in self.ebot._IDknown() if ID in x]:
                        with DB.DB(self.ebot, self.db):
                            self.ebot.uptime(ID)
                        c += 1
                        continue

                print("Working on %s out of %s" %
                      (c, total), end='\r')
                # Setting up dictionary for input
                r = session.get(self.japi + result['id'])
                assert r.status_code == 200, 'Bad URL: \n %s' % (self.japi + result['id'])
                # Gotta convert it to a soup
                dets = r.json()
                self.dict[ID] = {"Job ID": ID,
                                 "Title": result['title'],
                                 "Company": self.company,
                                 "URL": result['jobUrl'],
                                 "Catagory": result['slugs']['team'],
                                 "Posting date": result["lastUpdated"],
                                 "Location": result['city'] + ' ' + result['country']
                                 }
                self.dict[ID]["Description"] = dets['responsibilities'] if dets['responsibilities'] else 'None'
                self.dict[ID]["Basic Skills"] = dets['qualifications'] if dets['qualifications'] else 'None'
                self.dict[ID]["Pref Skills"] = 'None'
                c += 1
            print()
            print('pushing to database...')
            self.ebot.update(self.dict)
            print('database updated')
            self.dict = dict()
            with DB.DB(self.ebot, self.db):
                self.ebot.knownids = self.ebot._IDknown()



if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
