from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import dtemplate
import threading
import datetime
import DB
import selenium
import pickle
from bs4 import BeautifulSoup


class Scanner(dtemplate.Scanner):
    def __init__(self, *args, **kwargs):
        dtemplate.Scanner.__init__(self)
        self.company = 'Amazon'
        self.ipp = 10
        self.count = 0 
        self.tpattern = 'Posted %B %d, %Y'
        self.num = {'name': 'div', 'class_': 'col-sm-6 job-count-info'}
        self.kws = pickle.load(open('Scanners/keywords', 'rb'))
        self.cat = ["operations-it-support-engineering",
                    "project-program-product-management-technical",
                    "project-program-product-management-non-tech",
                    "marketing-pr",
                    "research-science",
                    "solutions-architect",
                    "business-intelligence",
                    "business-merchant-development",
                    "machine-learning-science",
                    "database-administration",
                    "systems-quality-security-engineering"]
        self.url = "https://www.amazon.jobs/en/search?offset=%s"\
            "0&result_limit=10&sort=relevant&category=%s&distanceType=Mi"\
            "&radius=24km&latitude=&longitude=&loc_group_id=&"\
            "loc_query=&base_query=%s&city=&"\
            "country=&region=&county=&query_options=&"
        self.bloat = "Amazon.com is an Equal "\
            "Opportunity-Affirmative Action Employer – Minority"\
            " / Female / Disability / Veteran / Gender Identity /"\
            " Sexual Orientation"
        self.jobs = "https://www.amazon.jobs/en/jobs/%s"
        self.dict = {}
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

    def page_scan(self, index):
        driver = self.driver
        driver.get(self.url % (index, self.ccat, self.kkw))
        response = driver.page_source
        soup = BeautifulSoup(response, 'lxml')
        rsu = soup.findAll('div', class_="location-and-id")
        dates = soup.findAll('h2', class_="posting-date")
        local_ids = [x.text for x in rsu]
        dates = [x.text for x in dates]
        local_ids = [x.split('|') for x in local_ids]
        local_ids = [[x[0][:-1], x[1][9:]] for x in local_ids]
        threads = []
        c = 0
        local_ids = [lid for lid in local_ids if not int(
            lid[1]) in self.ebot.knownids]
        # No local ids for some reason investigate
        if not local_ids:
            return False
        else:
            for loid in local_ids:
                if self.company + ' ' + loid[1] in self.ebot.knownids:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' + loid[1])
                    c += 1
                    continue
                if (not any([m in dates[c] for m in self.months])):
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' + loid[1])
                    c += 1
                    continue
                threads += [threading.Thread(name='thread handeling %s' % loid[1],
                                             target=self.mine,
                                             args=(loid[1],))]
                self.dict[self.company + ' ' + str(loid[1])] = {"Job ID": self.company + str(loid[1]),
                                                          "Company": self.company,
                                                          "Location": loid[0],
                                                          "Posting date": dates[c],
                                                          "Catagory": self.ccat}
                c += 1

            [imp.start() for imp in threads]
            [imp.join() for imp in threads]
            return True

    def mine(self, ide):
        driver = self.driver
        driver.get(self.jobs % ide)
        divs = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.title')))
        sects = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.xpath, "//div[@class='section']")))
        driver.close()
        # Attach to dictionary
        try:
            self.dict[self.company+' '+ str(ide)]["Title"] = divs.text
            self.dict[self.company+' '+ str(ide)]["Description"] = sects[0].text
            self.dict[self.company+' '+ str(ide)]["Basic Skills"] = sects[1].text
            self.dict[self.company+' '+ str(ide)]["URL"] = self.jobs % ide
            if len(sects) >= 3 and sects[2].text != 'JOIN US ON':
                self.dict[self.company+' '+ str(ide)]["Pref Skills"] = sects[2].text
            else:
                self.dict[self.company+' '+ str(ide)]["Pref Skills"] = "None"
        except Exception as ex:
            #print('a mine of %s failed trying again' % ide)
            self.count += 1
            if self.count <= 5:
                self.mine(ide)
            else:
                del self.dict[self.company+' '+ str(ide)]


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
