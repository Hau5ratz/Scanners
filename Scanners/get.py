import sys
import mechanize
import pickle

browser = mechanize.Browser()
browser.set_handle_robots(False)
cookies = mechanize.CookieJar()
browser.set_cookiejar(cookies)
browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]
browser.set_handle_refresh(False)
r = browser.open(sys.argv[1])
html = r.read()
with open('html', 'wb') as file:
    pickle.dump(html, file)
with open('check.txt', 'w') as file:
   file.write('just a check file')