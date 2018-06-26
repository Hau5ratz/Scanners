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
        self.tpattern = '%B %d, %Y'
        self.ipp = 20
        self.company = 'Amazon'
        self.kws = None
        self.num = {'name': 'span', 'id_icims': 'showing_jobs'}
        self.sapi = 'https://www.amazon.jobs/search.json?radius=24km&facets[]=location&facets[]=business_category&facets[]=category&facets[]=schedule_type_id&facets[]=employee_class&facets[]=normalized_city_name&facets[]=job_function_id&offset=0&result_limit=10000&sort=relevant&latitude=&longitude=&loc_group_id=&loc_query=&base_query=%s&city=&country=&region=&county=&query_options=&'
        self.japi = 'https://www.uber.com/api/jobs/'
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

    def initialize(self):
        os.system('clear')
        print('Starting %s scan' % self.company)
        for kw in self.kw:
            session = requests.Session()
            result = session.get(self.sapi % (kw))
            if result.status_code != 200:
                print('Did not get response from page')
                print('try again later or troubleshoot')
                exit()
            results = result.json()
            c = 0
            for result in results['jobs']:
                ID = self.company + ' ' + result['id_icims']
                with DB.DB(self.ebot, '/data/bookofjob.db'):
                    if [x for x in self.ebot._IDknown() if ID in x]:
                        with DB.DB(self.ebot, self.db):
                            self.ebot.uptime(ID)
                        c += 1
                        continue

                print("Working on %s out of %s" %
                      (c, results['hits']), end='\r')
                # Setting up dictionary for input
                #r = session.get(self.japi + result['id_icims'])
                #assert r.status_code == 200, 'Bad URL: \n %s' % (self.japi + result['id_icims'])
                # Gotta convert it to a soup
                #dets = r.json()
                self.dict[ID] = {"Job ID": ID,
                                 "Title": result['title'],
                                 "Company": self.company,
                                 "URL": result['url_next_step'],
                                 "Catagory": result['business_category'] if result['business_category'] else 'None',
                                 "Location": result['location']
                                 }
                self.dict[ID]["Posting date"] = result["posted_date"].lstrip(
                    '0') if '0' in result["posted_date"].split(' ')[1] else result["posted_date"]
                self.dict[ID]["Description"] = result['description'] if result['description'] else 'None'
                self.dict[ID]["Basic Skills"] = result['basic_qualifications'] if result['basic_qualifications'] else 'None'
                self.dict[ID]["Pref Skills"] = result['preferred_qualifications'] if result['preferred_qualifications'] else 'None'
                c += 1
            print('pushing to database...', end='\r')
            self.ebot.update(self.dict)
            print('database updated')
            self.dict = dict()
            with DB.DB(self.ebot, self.db):
                self.ebot.knownids = self.ebot._IDknown()


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
