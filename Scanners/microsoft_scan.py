import os
import damaz_scan
import threading
from bs4 import BeautifulSoup
import dryscrape
import DB
import pickle


def nlook(ide):
    return ''.join([c for c in ide if c.isdigit()])


class Scanner(damaz_scan.Scanner):
    def __init__(self):
        damaz_scan.Scanner.__init__(self)
        self.tpattern = '\n                            %d %b %Y\n                        '
        self.ipp = 20
        self.cwn = [2, 3, 1]
        self.company = 'Microsoft'
        self.kws = pickle.load(open('Scanners/keywords', 'rb'))
        self.cat = ['18','47','1','2','6','46','17','49','37',
                    '48','3','22','4','19','26','5', '27', '7',
                    '8','41','15','25','10','50','11', '9','20','24']
        self.num = {'name': 'span', 'class': 'resultRangeTop'}
        self.curl = ''

        self.url = "https://careers.microsoft.com/search.aspx"+\
        "#&&p2=all&p1=%s&p3=all&p4=all&p0=%s&p5=all&page=%s"
        self.db = "./data/bookofjob.db"
        if os.path.exists(self.db):
            print("WORKS")
        self.ebot = DB.DBM(self.db, self)
        with DB.DB(self.ebot, '/data/bookofjob.db'):
            self.ebot.knownids = self.ebot._IDknown()

    def page_scan(self, index):
        try:
            driver, server = self.serve()
            self.curl = self.url % (self.ccat, self.kkw, index)
            driver.visit(self.curl)
            print('Page url: %s' % self.curl)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".resultRangeTop")))
            response = driver.body()
            driver.reset()
            server.kill()
            soup = BeautifulSoup(response, 'lxml')
            results = soup.select('span[style="text-align: justify"]')
            c = 0
            local_ids = [nlook(lid['id']) for lid in results
                         if not self.company + nlook(lid['id']) in self.ebot.knownids]
            threads = []
            for loid in local_ids:
                if self.company + ' ' + loid in self.ebot.knownids:
                    with DB.DB(self.ebot, self.db):
                        self.ebot.uptime(self.company + ' ' + loid)
                    c += 1
                    continue
                threads += [threading.Thread(name='thread handeling %s' % loid,
                                             target=self.mine,
                                             args=(loid,))]
                self.dict[self.company + ' ' + str(loid)] = {"Job ID": self.company + ' ' + str(loid),
                                   "Company": self.company,
                                   "Posting date": soup.select_one('div[style="width: 85px;"]').text}
                self.ebot.knownids.append(loid)
                c += 1

            [imp.start() for imp in threads]
            [imp.join() for imp in threads]
        except dryscrape.mixins.WaitTimeoutError as ex:
            driver.reset()
            server.kill()
            
            print(self.url % (self.kkw, self.ccat, index))



    def mine(self, ide):
        try:
            driver, server = self.serve()
            url = "https://careers.microsoft.com/jobdetails.aspx?"+\
            "ss=&pg=0&so=&rw=1&jid=%s&jlang=EN&pp=SS"
            driver.visit(url % ide)
            print('Mine: %s' % (url % ide))
            ttok = 'ContentPlaceHolder1_JobDetails2_lblJobTitleText'
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#'+ ttok)))
            ltok = 'ContentPlaceHolder1_JobDetails2_lblLocationText'
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#'+ ltok)))
            ctok = 'ContentPlaceHolder1_JobDetails2_lblJobCategoryText'
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#'+ ctok)))
            dtok = 'ContentPlaceHolder1_JobDetails2_lblDescription'
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#'+ dtok)))

            response = driver.body()
            driver.reset()
            server.kill()
            soup = BeautifulSoup(response, 'lxml')

            title = soup.select('#'+ ttok)
            loc = soup.select('#'+ ltok)
            cat = soup.select('#'+ ctok)
            desc = soup.select('#'+ dtok)

            texty = [d.text for d in desc]


            self.dict[self.company+' '+ide]["Title"] = title[0].text
            self.dict[self.company+' '+ide]["Description"] = '\n'.join(texty).replace('\xa0','')
            self.dict[self.company+' '+ide]["Catagory"]: cat[0].text
            self.dict[self.company+' '+ide]["Location"] = loc[0].text
            self.dict[self.company+' '+ide]["URL"] = url % ide
            self.dict[self.company+' '+ide]["Basic Skills"] = 'None'
            self.dict[self.company+' '+ide]["Pref Skills"] = 'None'
        except dryscrape.mixins.WaitTimeoutError as ex:
            print('Proc %s timed out trying again for connection'%ide)
            print('restarting mine')
            self.mine(ide)


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
    print("Finished completely")
