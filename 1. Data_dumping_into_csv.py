import json
import random
import time
import urllib
import urllib2
from datetime import datetime, timedelta
from io import StringIO
import re
import brotli
import cfscrape
import requests
import requests.exceptions
from bs4 import BeautifulSoup
from lxml import etree, html
from selenium import webdriver
#from selenium.common.exceptions import NoSuchElementException
#from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.support.ui import WebDriverWait
#from xvfbwrapper import Xvfb
from pyvirtualdisplay import Display
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
def is_bad_proxy(pip,url):    
    try:        
        res = requests.get(url,proxies={'http':pip},headers={'User-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'},timeout=10)
    except Exception, detail:
        print "ERROR:", detail
        return 1
    if res.status_code ==200:
        return 0
    else:
        print res.status_code
        return 1

def get_proxys():
    url = 'https://hidemy.name/ru/loginx'
    url1 = 'https://hidemy.name/api/proxylist.txt?out=plain&lang=ru'
    data = {'c':'976402971148490'}
    s = requests.session()
    s.get(url1)
    s.post(url,data=data)
    res = s.get(url1)
    result = res.text.split('\r\n')
    return result
def validate_proxies(proxies,url):
    proxys = []
    random.shuffle(proxies)
    stime = datetime.now()+timedelta(minutes=30)
    for proxy in proxies:
        if stime < datetime.now():
            break
        bad_proxy = is_bad_proxy(proxy,url)
        if not bad_proxy:
            print proxy, "APPROVED!"
            proxys.append({'http':proxy})
            if len(proxys)==10:
                break
	elif str(bad_proxy)[0]=='5' and len(proxys)==0:
	    print 'This service is now unavailable (site from scraping is unavailable)'
    if len(proxys)==0:
        return 0
    return proxys
def choice_proxy(proxies):
    return proxies[random.randint(0,len(proxies)-1)]
def paged(string):
    htmlparser = etree.HTMLParser()
    return etree.parse(StringIO(string),htmlparser)
def scrape(next_page_url,lxml_grab=None,proxies=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    if proxies !=0 and len(proxies)>0:
        plist = proxies[:]
        status_code=0
        while len(plist)>0 and status_code!=200:
            choiced = choice_proxy(plist)
            try:
                response = requests.get(next_page_url, headers=headers,timeout=10,proxies=choiced)
                status_code=response.status_code
            except:
                pass
            plist.remove(choiced)
    else:
        response=requests.get(next_page_url, headers=headers,timeout=10)
        if response.status_code !=200:
            return 0
    if lxml_grab is None:
        soup = BeautifulSoup(response.text, "html5lib")
    else:
        soup = paged(response.text)
    return soup

def request(date,viewstate,eventValidation,proxies=None):
    url = "http://tickets.fgcineplex.com.sg/visInternetTicketing/visShowtimes.aspx"
    payload = "__EVENTTARGET=ddlFilterDate&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE="+urllib.quote_plus(viewstate)+"&__EVENTVALIDATION="+urllib.quote_plus(eventValidation)+"&ddlFilterDate="+date+"&radListBy=radListByCinema"
    headers = {
        'cookie': "AspxAutoDetectCookieSupport=1; ASP.NET_SessionId=pax3ay5515svju45dd2hgm2x; __utma=200437049.338039226.1512312200.1512312200.1512312200.1; __utmc=200437049; __utmz=200437049.1512312200.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); visSessionID=5236dbce0391413eaf105078af107962",
        'origin': "http://tickets.fgcineplex.com.sg",
        'accept-encoding': "gzip, deflate",
        'accept-language': "en-US,en;q=0.8",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'cache-control': "no-cache",
        'referer': "http://tickets.fgcineplex.com.sg/visInternetTicketing/visShowtimes.aspx",
        'connection': "keep-alive",
        'postman-token': "57b3b197-a7e9-799c-403d-6133223c739d"
    }
    proxys = proxies[:]
    status_code=0
    while len(proxys)>0 and status_code!=200:
        print proxys
        choiced = choice_proxy(proxys)
        proxys.remove(choiced)
        try:
            response = requests.request("POST", url, data=payload, headers=headers,proxies=choiced)
            status_code = response.status_code
        except:
            print 'Cant load with proxy'
            pass
    
    if status_code !=200:
        try:
            print 'Cant connect via proxy, trying connect directly'
            response = requests.request("POST", url, data=payload, headers=headers)
        except:
            return 0
    return response

def scrapeurl(date,viewstate,eventValidation,proxies=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = request(date,viewstate,eventValidation,proxies)
    if response!=0:
        soup = BeautifulSoup(response.text, "html5lib")
    else:
        return 0
    return soup

def requestShaw(viewstate,date,proxies=None):
    url = "http://www.shaw.sg/sw_buytickets.aspx"
    payload = "__EVENTTARGET=ctl00%24Content%24ddlShowDate&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE="+urllib.quote_plus(viewstate)+"&__VIEWSTATEGENERATOR=0500EEBB&__VIEWSTATEENCRYPTED=&CplexCode=&FilmCode=&ctl00%24Content%24ddlShowDate="+urllib.quote_plus(date)+"&ctl00%24Content%24rblSelectSeating=M&ctl00%24Content%24txtAvail=&ctl00%24Content%24txtSellFast=&ctl00%24Content%24txtSoldOut="
    headers = {
        'cookie': "ASP.NET_SessionId=sdi1lk553tmoz545mpazuxzw; cookieCheck=12/3/2017 8:51:13 PM; __utmt=1; __utma=196025459.800268039.1512305405.1512311797.1512321588.4; __utmb=196025459.9.10.1512321588; __utmc=196025459; __utmz=196025459.1512321588.4.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __atuvc=18%7C49; __atuvs=5a243232620ce92b008",
        'origin': "http://www.shaw.sg",
        'accept-encoding': "gzip, deflate",
        'accept-language': "en-US,en;q=0.8",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'cache-control': "no-cache",
        'referer': "http://www.shaw.sg/sw_buytickets.aspx",
        'connection': "keep-alive",
        'postman-token': "6eb3446a-f9f2-1f8a-6743-a4e5f3b8dcd5"
    }
    if proxies!=0:
        response = requests.request("POST", url, data=payload, headers=headers,proxies=choice_proxy(proxies))
    else:
        print "Can't get response from unavailable %s (Error code 5XX)"%url
        return 0
    return response

def scrapeUrlshaw(viewstate,date,proxies=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requestShaw(viewstate,date,proxies)
    if response!=0:
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        return 0
    return soup

def getCinemas(proxies=None):
    url = "https://www.gv.com.sg/.gv-api/cinemas"
    headers = {
            'origin': "https://www.gv.com.sg",
            'accept-encoding': "gzip, deflate, br",
            'x_developer': "ENOVAX",
            'accept-language': "en-US,en;q=0.8",
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            'content-type': "application/json; charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'referer': "https://www.gv.com.sg/GVBuyTickets",
            'authority': "www.gv.com.sg",
            #'cookie': "__cfduid=d848fb1f803ddc4406880fd4dfceb7eca1511894040; __atuvc=1%7C49; JSESSIONID=0GRgIfUqqxpuAKKEsKrO95dt.undefined; _ga=GA1.3.640411893.1511894050; _gid=GA1.3.1043315194.151230618$
            'cookie' : "__cfduid=db4aa507ed20675598e5500ff69d2dc841525162952; _ga=GA1.3.1520606575.1525163281; _gid=GA1.3.638964924.1525163281; _gat=1; publica_session_id=ef4d7367-4966-3ac1-c21b-b2ca57c6ec72; JSESSIONID=20AA6103A27DE2F707B4D624064B18EE",
            'cache-control': "no-cache",
            'path': '/.gv-api/v2buytickets?t=387_1525167473252'
            #'postman-token': "872dd435-61f6-8021-6e2f-cc9fba3a40cf"
    }
    headers = {
            'origin': 'https://www.gv.com.sg',
            'content-type': 'application/json; charset=UTF-8',
            'referer': 'https://www.gv.com.sg/GVBuyTickets',
            'x_developer': 'ENOVAX',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    #proxies = validate_proxies(proxies,url)
    if proxies!=0:
        response = requests.request("POST", url, headers=headers,proxies=choice_proxy(proxies))#, proxies=proxyDict)
    else:
        response = requests.request("POST", url, headers=headers)
    try:
        data_return = (brotli.decompress(response.content))
    except:
        data_return = response.content
    #print data_return.decode('utf-8')
    print response.text
    data = json.loads(data_return)
    cinemas={}
    for i in data['data']:
        cinemas[i['id']] = i['name']
    return cinemas

def timeConvert(timeStr):
    time = timeStr.split(':')
    type = ''
    if (int(time[0]) > 11):
        if (int(time[0]) == 12):
            time = time[0] + ":" + time[1]
        else:
            time = str(int(time[0]) - 12) + ':' + time[1]
        type = ' PM'
    else:
        time = time[0] + ':' + time[1]
        type = ' AM'
    return time+type

def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

def dateConvert(dateStr):
    date = dateStr.split(' ')
    month = str(month_string_to_number(date[2]))
    year = str(datetime.now().year)
    return date[1]+'/'+month+'/'+year

def fileWrite(string):
    print string
    data.append(string)

def carnival(proxies=None):
    print "<<<<< carnival cinema process started >>>>>"
    headers = {
        'Accept':'application/json, text/plain, */*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-GB,en;q=0.5',
        'Host':'service.carnivalcinemas.sg',
        'Origin':'https://carnivalcinemas.sg',
        'Referer':'https://carnivalcinemas.sg/',
        'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux) Gecko/20100101 Firefox/60.0',
        'Token':'bXpFNVc2bHR1d3IvK3lSb3F3UHVFVDJqNE8rN2VWN3ZiNEJ0Mnd3TXorbz18aHR0cHM6Ly9jYXJuaXZhbGNpbmVtYXMuc2cvIy9ib29rU2VhdHw2MzY2NjEzNDAwNzA2MzAwMDB8cno4THVPdEZCWHBoajlXUWZ2Rmg='
    }
    MAIN_URL = 'https://carnivalcinemas.sg/#'
    proxies = validate_proxies(proxies,MAIN_URL+'/')
    allmov_url = 'http://service.carnivalcinemas.sg/api/QuickSearch/GetAllMovieDetail?locationName=Mumbai'
    sdates_url = 'http://service.carnivalcinemas.sg/api/QuickSearch/GetShowDatesByMovies?location=Mumbai&movieCode={0}'
    times_url = 'http://service.carnivalcinemas.sg/api/QuickSearch/GetCinemaAndShowTimeByMovie?location=Mumbai&movieCode={0}&date={1}'
    link = 'https://carnivalcinemas.sg/#/{0}/{1}'
    if len(proxies)>0:
        ss = requests.session()
        ss.headers = headers
        ss.proxies = random.choice(proxies)
        ss.timeout = 10
    else:
        ss = requests.session()
        ss.headers = headers
    try:
        res_am = json.loads(ss.get(allmov_url).content)['responseMovies']
    except Exception as e:
        print e
        raise Exception
    for film in res_am:
        fname = film['name']
        try:
            dates = json.loads(ss.get(sdates_url.format(fname)).content)['responseShowDates']
        except Exception as e:
            print e
            continue
        for date in dates:
            qdate = date['showDateValue']
            try:
                times = json.loads(ss.get(times_url.format(fname,qdate)).content)['responseCinemaWithShowTime']
            except Exception as e:
                print e
                continue
            for t in times:
                cinemaname = ' '.join(t['cinemaName'].split()[2:])
                if cinemaname.count('Shaw Tower'):
                    cinemaname = 'Beach Road'
                dd = qdate.split('T')[0].split('-')
                dd.reverse()
                if t['showTime'].count(','):
                    ts = [x.strip()[:-1] for x in t['showTime'].split(',')]
                    for ti in ts:
                        ti.strip()
                        if ti.count('T'):
                            ti = ti[:-1]
                        line = '"' + fname.strip() + '","' + cinemaname + '","' + 'Carnival' + '","' + '/'.join(dd) + '","' + ti.strip() + '","' + link.format(fname,fname).replace(' ','%20') + '"'
                        fileWrite(line)
                else:
                     line = '"' + fname.strip() + '","' + cinemaname + '","' + 'Carnival' + '","' + '/'.join(dd) + '","' + t['showTime'].strip()[:-1] + '","' + link.format(fname,fname).replace(' ','%20') +'"'
                     fileWrite(line)
    '''status = 0
    #vdisplay = Xvfb()
    #vdisplay.start()
    if proxies == 0:
        print "Can't get data from unavailable service %s"%MAIN_URL
        c_ops = webdriver.ChromeOptions()
        #c_ops.add_argument('--proxy-server=%s' % choice_proxy(proxies)['http'])
        c_ops.add_argument('--no-sandbox')
        #c_ops.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=c_ops)
        #driver = webdriver.Chrome()
        #driver = webdriver.Firefox('/usr/local/bin',capabilities=cap)
    else:
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': choice_proxy(proxies)['http'],
            'ftpProxy': choice_proxy(proxies)['http'],
            'sslProxy': choice_proxy(proxies)['http'],
             'noProxy': '' # set this value as desired
        })
        c_ops = webdriver.ChromeOptions()
        c_ops.add_argument('--proxy-server=%s' % choice_proxy(proxies)['http'])
        c_ops.add_argument('--no-sandbox')
        #c_ops.add_argument('--headless') 
        driver = webdriver.Chrome(chrome_options=c_ops) #service_log_path='/home/sriabt/databaseUpload/chdvr.log')
        #driver = webdriver.Firefox('/usr/local/bin',capabilities=cap)
    def get_times(driver,page):
        counter = 0
        result = []
        days = page.xpath('//div[@class="now-playing clearfix"]/div[@class="movies-date clearfix"]/ul[@class="tab clearfix "]/li/a/text()')
        for day in days:
            if counter ==0:
                times = page.xpath('//ul[@class="movies-time"]/li/a/text()')
            else:
                driver.find_element_by_xpath('//div[@class="now-playing clearfix"]/div[@class="movies-date clearfix"]/ul[@class="tab clearfix "]/li[%s]/a'%str(counter+1)).click()
                time.sleep(10)
                times = page.xpath('//ul[@class="movies-time"]/li/a/text()')
            result.append({"day":day,'times':times})
            counter +=1
        return result
    try:
        driver.get("https://carnivalcinemas.sg/#/Movies")
        time.sleep(40)
        res = driver.page_source
        page = paged(res)
        #print res
        for movie in page.xpath('//div[@class="movies"]'):
            title = movie.xpath('div/h2')[0].text
            print title
            status = 1
            detail_url = MAIN_URL + movie.xpath('a[last()]/@href')[0]
            driver.get(detail_url)
            time.sleep(20)
            res = driver.page_source
            dpage = paged(res)
            theatre = dpage.xpath('//div[@class="col-sm-4 theaters"]/text()')[0]
            data = get_times(driver,dpage)
            for day in data:
                date = dateConvert(day['day'])
                for timeo in day['times']:
                    line = '"' + title.strip() + '","' + 'Beach Road'  + '","' + theatre + '","' + date + '","' + timeo.strip() + '","' + detail_url + '"'
                    #print line
                    fileWrite (str(line.encode('ascii', 'ignore').decode('ascii')) )
        #driver.quit()
        #vdisplay.stop()
    except Exception as e:
        print(e)
        warnings.append('(Carnival) Error extraction')
        #driver.quit()
        #vdisplay.stop()
        raise ParseError'''
    print "<<<<< carnival cinema process ended >>>>>"
    #return status
def cathay(proxies = None):
    print "<<<<< cathay cinema process started >>>>>"
    url = "http://www.cathaycineplexes.com.sg/showtimes.aspx"
    proxies = validate_proxies(proxies,url)
    sess = requests.session()
    plist=proxies[:]
    status=0
    while len(plist)>0 and status!=200:
        choiced = choice_proxy(plist)
        sess.proxies = choiced
        sess.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        scraper = cfscrape.create_scraper(sess,delay=40)
        try:
            response = scraper.get(url)
            status = response.status_code
            #print response.content
            soup = paged(response.text)
        except Exception as e:
            print e
            status = 0
        plist.remove(choiced)
    if status!=200:
        sess = request.session()
        scraper = cfscrape.create_scraper(sess,delay=40)
        response = scraper.get(url)
        try:
            soup = paged(response.text)
        except Exception as e:
            print e
            return 0
    divArray = ['ContentPlaceHolder1_wucST_tabs', 'ContentPlaceHolder1_wucST1_tabs',
                'ContentPlaceHolder1_wucST2_tabs', 'ContentPlaceHolder1_wucST3_tabs', 'ContentPlaceHolder1_wucST4_tabs',
                'ContentPlaceHolder1_wucST5_tabs', 'ContentPlaceHolder1_wucST6_tabs',
                'ContentPlaceHolder1_wucSTPMS_tabs']
    titles = ['AMK HUB','CAUSEWAY POINT', 'CINELEISURE ORCHARD', 'DOWNTOWN EAST', 'JEM', 'PARKWAY PARADE','THE CATHAY', 'WEST MALL','Platinum Movie Suite']
    for i in range(0, len(divArray)):
        div = divArray[i]
        title = titles[i]
        try:
            tabs = soup.xpath('//div[@id="%s"]'%div)[0]
            dates = tabs.xpath('ul/li/a/span[@class="smalldate"]/text()')
            #print dates
            containers = tabs.xpath('div[@class="tabbers"]')
            for i in xrange(0, len(containers)):
                movie_containers =  containers[i].xpath('div')
                date = dates[i]
                timediv = date.split(' ')
                date = str(timediv[0]) + '/' + str(month_string_to_number(timediv[1])) + '/' + str(datetime.now().year)
                for j in xrange(0, len(movie_containers)):
                    hall = ''
                    hall_div = movie_containers[j].xpath('div[@class="movie-desc"]/strong')
                    if (len(hall_div) > 1):
                        hall = hall_div[0].text
                    film = ''
                    film_div = movie_containers[j].xpath('div[@class="movie-desc"]/span[@class="mobileLink"]/strong/a')
                    if (len(film_div) > 0):
                        film = film_div[0].text
                        #print film
                    if (film == ''):
                        continue
                    if (hall == ''):
                        hall = title
                        #print title
                    times = movie_containers[j].xpath('div[@class="movie-timings"]/div[@class="showtimeitem_time_pms"]/a')
                    #print film
                    #print [html.tostring(time) for time in times]
                    for k in times:
                        if k.get('data-href') is None:
                            continue
                        #print film
                        #print film.strip()
                        #print k.xpath('span[1]')[0].text
                        #print k.xpath('span[1]/text()') 
                        line = '"' + film.strip() + '","' + title + '","' + hall + '","' + date + '","' + k.xpath('span[1]')[0].text.strip() + '","' + k.get('data-href') + '"'
                        line = line.encode('ascii', 'ignore')
                        #print line
                        fileWrite(line )
        except Exception as e:
            warnings.append('(Cathay) Error extraction %s '%(title))
            print(e)
            raise ParserError
    print "<<<<< cathay cinema process ended >>>>>"
    
def fg(proxies=None):
    print "<<<<< fg cinema process started >>>>>"
    url = "http://tickets.fgcineplex.com.sg/visInternetTicketing/"
    baseUrl = "http://tickets.fgcineplex.com.sg/visInternetTicketing/"
    proxies = validate_proxies(proxies,url)
    soup = scrape(url,proxies=proxies)
    if soup == 0:
        return 0
    #print soup
    optionList = soup.select('select.ShowtimesFilterDropDownList > option')
    viewState = soup.select('input#__VIEWSTATE')[0]['value']
    eventValidation = soup.select('input#__EVENTVALIDATION')[0]['value']
    for k in optionList:
        date = k['value']
        print date
        soup = scrapeurl(date, viewState, eventValidation,proxies=proxies)
        #print soup
        tr = soup.select('table#tblMovieShowtimes > tbody > tr')
        for i in tr:
            className = i.get('class')
            if (className != None):
                className = className[0]
            if (className == 'ShowtimesCinemaRow'):
                hall = i.select('span.ShowtimesCinemaName')[0].text
            elif (className == 'ShowtimesSummaryRow'):
                film = i.select('a.ShowtimesMovieLink')[0].text
                times = i.select('a.ShowtimesSessionLink')
                for j in times:
                    time = j.text
                    link = baseUrl + j['href']
                    line = '"' + film + '","' + hall + '","' + hall + '","' + date + '","' + time + '","' + link + '"'
                    #print line
                    fileWrite(line )
            elif (className == 'ShowtimesSummaryRowAlt'):
                film = i.select('a.ShowtimesMovieLink')[0].text
                times = i.select('a.ShowtimesSessionLink')
                for j in times:
                    time = j.text
                    link = baseUrl + j['href']
                    line = '"' + film + '","' + hall + '","' + hall + '","' + date + '","' + time + '","' + link + '"'
                    #print line
                    fileWrite(line )
    print "<<<<< fg cinema process ended >>>>>"
def gv(proxies=None):
    print "<<<<< gv cinema process started >>>>>"
    proxies = validate_proxies(get_proxys(),"https://www.gv.com.sg")
    dateArray = []
    dateArray.append(int(time.mktime(datetime.now().date().timetuple()) * 1000))
    for i in xrange(1, 7):
        newDate = (datetime.now() + timedelta(days=i)).date()
        unixtime = time.mktime(newDate.timetuple())
        dateArray.append(int(unixtime * 1000))
    for j in dateArray:
        sess = requests.session()
        if proxies !=0:
            sess.proxies = {'http':choice_proxy(proxies)}
            sess.headers = {'User-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        scraper = cfscrape.create_scraper(sess,delay = 15)
        url = "https://www.gv.com.sg/.gv-api/v2buytickets"
        print (str(j))
        payload = '{"cinemaId":"","filmCode":"","date":' + str(j) + ',"advanceSales":false}'
        headers = {
            'origin': "https://www.gv.com.sg",
            'accept-encoding': "gzip, deflate, br",
            'x_developer': "ENOVAX",
            'accept-language': "en-US,en;q=0.8",
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            'content-type': "application/json; charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'referer': "https://www.gv.com.sg/GVBuyTickets",
            'authority': "www.gv.com.sg",
            #'cookie': "__cfduid=d848fb1f803ddc4406880fd4dfceb7eca1511894040; __atuvc=1%7C49; JSESSIONID=0GRgIfUqqxpuAKKEsKrO95dt.undefined; _ga=GA1.3.640411893.1511894050; _gid=GA1.3.1043315194.1512306186; _gat=1",
            'cookie' : "__cfduid=db4aa507ed20675598e5500ff69d2dc841525162952; _ga=GA1.3.1520606575.1525163281; _gid=GA1.3.638964924.1525163281; _gat=1; publica_session_id=ef4d7367-4966-3ac1-c21b-b2ca57c6ec72; JSESSIONID=20AA6103A27DE2F707B4D624064B18EE",
            'cache-control': "no-cache",
            'path': '/.gv-api/v2buytickets?t=387_1525167473252'
            #'postman-token': "872dd435-61f6-8021-6e2f-cc9fba3a40cf"
        }
        headers = {
            'origin': 'https://www.gv.com.sg',
            'content-type': 'application/json; charset=UTF-8',
            'referer': 'https://www.gv.com.sg/GVBuyTickets',
            'x_developer': 'ENOVAX',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        }
        try:
            response = scraper.post(url, data=payload, headers=headers)
            #print response.content
        except Exception as e:
            print(e)
            warnings.append('(Gv) Error extraction %s '%(str(j)))
        try:
            data_return = ((response.content))
        except:
            continue
        data = json.loads(data_return)
        halls = (data['data']['cinemas'])
        cinemas = getCinemas(proxies=proxies)
        for j in halls:
            hall = cinemas[j['id']]
            for k in j['movies']:
                film = k['filmTitle']
                for n in k['times']:
                    timeNow = n['time12'][:-2]+' '+n['time12'][-2:]
                    date = n['showDate'].replace('-','/')
                    link = "https://www.gv.com.sg/GVSeatSelection#/cinemaId/" + j['id'] + "/filmCode/" + k['filmCd'] + "/showDate/" + n['showDate'] + "/showTime/" + n['time24'] + "/hallNumber/" + n['hall']
                    line = '"' + film.strip() + '","' + hall + '","' + hall + '","' + date + '","' + timeNow.strip() + '","' + link + '"'
                    #print line
                    fileWrite(str(line.encode('ascii', 'ignore').decode('ascii')) )
    print "<<<<< gv cinema process ended >>>>>"

def shaw(proxies = None):
    print "<<<<< shaw cinema process started >>>>>"
    url = "http://www.shaw.sg/sw_buytickets.aspx"
    baseUrl = "http://www.shaw.sg/"
    proxies = validate_proxies(proxies,url)
    soup = scrape(url,proxies=proxies)
    if soup ==0:
        return 0
    viewState = soup.select('input#__VIEWSTATE')[0]['value']
    optionList = soup.select('select#ctl00_Content_ddlShowDate > option')
    for k in optionList:
        date = k['value']
        print date
        try:
            soup = scrapeUrlshaw(viewState, date,proxies=proxies)
            date = date.split('/')
            date = date[1] + '/' + date[0] + '/' + date[2]
            schedules = soup.select('table.panelSchedule')
            hall = ''
            film = ''
            for i in schedules:
                filmDiv = i.select('td.txtScheduleHeaderCineplex')
                if (len(filmDiv) > 0):
                    hall = filmDiv[0].text.split('(')[0].encode('ascii', 'ignore')
                else:
                    timeDiv = i.select('a.txtSchedule')
                    if (len(timeDiv) > 0):
                        film = timeDiv[0].text
                        for j in timeDiv[1:]:
                            time = j.text
                            time = time[:time.index('M') + 1]
                            link = ("http://www.shaw.sg/" + j['href'])
                            link = link.replace('/imax/index.htm?page=seatselect&', '/imax_ticketing/sw_seatselect.aspx?')
                            link = link.replace('/premiere/movies.html?page=seatselect&',
                                                '/premiere_ticketing/sw_seatselect.aspx?')
                            link = link.replace(' ', '%20')
                            line = '"' + film + '","' + hall + '","' + hall + '","' + date + '","' + time + '","' + link + '"'
                            #print line
                            fileWrite(line )
        except Exception as e:
            warnings.append('(Gv) Error extraction %s '%(str(date)))
            print(e)
    print "<<<<< shaw cinema process ended >>>>>"
    
def we(proxies=None):
    print "<<<<< we cinema process started >>>>>"
    url = "https://www.wecinemas.com.sg/buy-ticket.aspx"
    proxies = validate_proxies(proxies,url)
    soup = scrape(url,proxies=proxies,lxml_grab=True)
    if soup ==0:
        return 0
    days = soup.xpath('/html/body/form/div[6]/table/tr/td/div/div/div[7]/div/table/tr[2]/td/table/tr/td[1]/table/tr[1]/td/table/tr/td/table/tr[6]/td/table/tr/td/table/tr[5]/td/table/tr/td/table/tr/td/table')
    for day in xrange(len(days)):
        date = days[day].xpath('tr[1]/td/div[@class="showtime-date-con"]/div[@class="showtime-date"]/text()')[0].split(' ')
        date = '/'.join([str(date[0]),str(month_string_to_number(date[1])),str(date[2].split(',')[0])])
        dm = soup.xpath('/html/body/form/div[6]/table/tr/td/div/div/div[7]/div/table/tr[2]/td/table/tr/td[1]/table/tr[1]/td/table/tr/td/table/tr[6]/td/table/tr/td/table/tr[5]/td/table/tr/td/table/tr[%s]/td/table/tr[3]/td'%str(day+1+2*day))
        for x in xrange(len(dm[0].xpath('table/tr'))):
            fname = dm[0].xpath('table/tr[%s]/td/h3/a/text()'%str(2+7*x))
            if len(fname)>0:
                times = dm[0].xpath('table/tr[%s]/td/table/tr[2]/td/div[@class="showtimes-but"]/a'%str(5+7*x))
                for t in times:
                    if fname[0].count('First Class'):
                        hall = '321 Clementi (First Class)'
                    else:
                        hall = '321 Clementi'
                    line = '"' + fname[0] + '","' + hall + '","' + 'WE-Clementi' + '","' + date + '","' + ' '.join([re.findall('\d+:\d+',t.text)[0],t.text[-2:]]) + '","' + t.xpath('@href')[0] + '"'
                    fileWrite(line)
    print "<<<<< we cinema process ended >>>>>"


TRYING_QUOTA    = 5
data            = []
proxies         = get_proxys()
warnings        = []

shaw_status     = 0
carnival_status = 0
cathay_status   = 0
fg_status       = 0
we_status       = 0
gv_status       = 0


start_time = datetime.now()
##########  SHAW  ####################
shaw_counter = 0
while shaw_status == 0 and TRYING_QUOTA > shaw_counter:
    try:
        shaw(proxies=proxies)
        shaw_status = 1
    except Exception as e:
        print e
        warnings.append("Shaw error scraping")
    shaw_counter +=1

#########  CARNIVAL ##################
carnival_counter=0
#display = Display(visible=0, size=(800, 600))
#display.start()
while carnival_status == 0 and TRYING_QUOTA > carnival_counter:
    try:
        carnival(proxies=proxies)
        carnival_status = 1
    except Exception as e:
        print e
        warnings.append("Carnival error scraping")
    carnival_counter += 1

#display.stop()
#########  CATHAY  ###################
cathay_counter = 0
while cathay_status == 0 and TRYING_QUOTA > cathay_counter:
    try:
        cathay(proxies=proxies)
        cathay_status = 1
    except Exception as e:
        print(e)
        warnings.append("Cathay error scraping")
    cathay_counter +=1

########  FG  ##########################
fg_counter = 0
while fg_status == 0 and TRYING_QUOTA > fg_counter:
    try:
        fg(proxies=proxies)
        fg_status = 1
    except Exception as e:
        print e
        warnings.append("Fg error scraping")
    fg_counter += 1

######## WE ############################
we_counter = 0
while we_status == 0 and TRYING_QUOTA > we_counter:
    try:
        we(proxies=proxies)
        we_status = 1
    except Exception as e:
        print e
        warnings.append("We error scraping")
    we_counter += 1

########  GV  #########################
gv_counter = 0
while gv_status == 0 and TRYING_QUOTA > gv_counter:
    try:
        gv(proxies=proxies)
        gv_status = 1
    except Exception as e:
        print e
        warnings.append("Gv error scraping")
    gv_counter +=1
#######################################
end_time = datetime.now()


for war in warnings:
    print war

data = list(set(data))
with open('/home/sriabt/databaseUpload/movie_data.csv','w') as f:
    for i in data:
        f.write(i+'\n')


print 'Working time - ',end_time - start_time
print end_time
print "##########################################"
print "Script ends"
print "##########################################"

