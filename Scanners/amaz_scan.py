import template
import threading
import datetime

class Scanner(template.Scanner):
    def __init__(self, *args, **kwargs):
        template.Scanner.__init__(self)
        self.company = 'Amazon'
        self.numxpath = '//*[@id="main-content"]/div[3]/div/div/div[2]/content/div/div/div[2]/div[1]/div[1]'
        self.kws = ["software development",
                    "solutions architect",
                    "merchant services",
                    "amazon pay",
                    "wallet",
                    "digital payment",
                    "ACH",
                    "credit ",
                    "debit"]
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


    def page_scan(self, index):
        driver = self.d(executable_path=self.path)
        driver.get(self.url % (index, self.ccat, self.kkw))
        rsu = driver.find_elements_by_class_name("location-and-id")
        dates = driver.find_elements_by_class_name("posting-date")
        local_ids = [x.text for x in rsu]
        dates = [x.text for x in dates]
        driver.close()
        local_ids = [x.split('|') for x in local_ids]
        local_ids = [[x[0][:-1], x[1][9:]] for x in local_ids]
        threads = []
        c = 0
        local_ids = [lid for lid in local_ids if not int(
            lid[1]) in self.ebot.knownids]
        for loid in local_ids:
            if loid[1] in self.ebot.knownids:
                c += 1
                continue
            if (not any([m in dates[c] for m in self.months]) or "2017" not in dates[c]):
                c += 1
                continue
            threads += [threading.Thread(name='thread handeling %s' % loid[1],
                                         target=self.mine,
                                         args=(loid[1],))]
            self.dict[loid[1]] = {"Job ID": loid[1],
                                  "Company": self.company,
                                  "Location": loid[0],
                                  "Posting date": dates[c],
                                  "Catagory": self.ccat}
            c += 1
        [imp.start() for imp in threads]
        [imp.join() for imp in threads]

    def mine(self, ide):
        driver = self.d(executable_path=self.path)
        driver.get(self.jobs % ide)
        div = driver.find_element_by_xpath(
            '''//*[@id="job-detail"]/div[1]/div/div/div[1]/div/h1''')
        self.dict[ide]["Title"] = div.text
        sects = driver.find_elements_by_class_name("section")
        text = sects[1].text
        if self.bloat in text:
            text = text[:text.index(self.bloat)]
        self.dict[ide]["Description"] = sects[0].text
        self.dict[ide]["Basic Skills"] = text
        self.dict[ide]["URL"] = self.jobs % ide
        if len(sects) >= 3 and sects[2].text != 'JOIN US ON':
            self.dict[ide]["Pref Skills"] = sects[2].text
        else:
            self.dict[ide]["Pref Skills"] = "None"
        driver.close()


if __name__ == "__main__":
    app = Scanner()
    app.initialize()
