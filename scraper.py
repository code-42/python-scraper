#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as soup
from pymongo import MongoClient
import time
import os
import re

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0")
driver = webdriver.Firefox(profile)
# driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10) # seconds

loginUrl = os.environ.get('YAHOO_LOGIN_URL')
username = os.environ.get('YAHOO_USERNAME')
password = os.environ.get('YAHOO_PASSWORD')
watchlistUrl = os.environ.get('YAHOO_WATCHLIST_URL')
mongo_dbname = os.environ.get('MONGO_DBNAME')
mongo_uri = os.environ.get('MONGO_URI')

# current date and time
timeStamp = datetime.now().timestamp()
print("timestamp == ", timeStamp)
dt = datetime.now().strftime("%b %d, %Y @ %I:%M %p")
print("dt == ", dt)

# html returned from get_page()
page_html = ""
# dict to be inserted into mongodb
total_values = {}
# watchlist is a list of dicts
watchlist = []


# login to get handle on driver
def login(driver):
    # log into yahoo finance and return a handle to webdriver
    try:
        print(loginUrl)
        driver.get(loginUrl)

        # the internet is slow so wait until the login box is ready
        signIn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-username"]')))
        elem = driver.find_element_by_xpath('//*[@id="login-username"]')
        elem.clear()
        elem.send_keys(username)
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-signin"]')))
        elem = driver.find_element_by_xpath('//*[@id="login-signin"]').click()

        elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-passwd"]')))
        elem = driver.find_element_by_xpath('//*[@id="login-passwd"]')
        elem.clear()
        elem.send_keys(password)
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-signin"]')))
        elem = driver.find_element_by_xpath('//*[@id="login-signin"]').click()
       
        # elem = wait.until(EC.title_contains(driver.title))
        driver.get(watchlistUrl)

        # elem = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/dialog/section/button')))
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/dialog/section/button')))
        if(elem):
            print(elem)
            driver.find_element_by_xpath('/html/body/dialog/section/button').click()

        return driver

    except Exception as e:
        # print(str(e))
        pass
    except TimeoutException:
        pass


def save_page(driver):
    # open connection and grab the page
    elem = driver.find_element_by_xpath("//*")
    page_html = elem.get_attribute("outerHTML")
    try:
        filename = "watchlist.html"
        f = open(filename, 'w', encoding='utf-8')
        f.write(page_html)
    finally:
        # close the file watchlist.html - is done writing
        f.close()
        # no longer need webdriver
        driver.close()
        driver.quit()
        # print(page_html)
        return page_html

def make_soup():
    filename = "watchlist.html"
    with open(filename, 'r', encoding='utf-8') as f:
        contents = f.read()
        # contents = page_html
        soup = BeautifulSoup(contents, 'lxml')
        print(type(soup))
        f.close()
        return soup


# def scrape_totals(page_html):
def scrape_totals():
    keys = ['Market Time','Total Value','Day Gain','Total Gain'] 
    values = []
    try:
        # first item in list is market time
        values.append(dt)
        # filename = "watchlist.html"
        # with open(filename, 'r', encoding='utf-8') as f:
        #     contents = f.read()
        #     # contents = page_html
        #     soup = BeautifulSoup(contents, 'lxml')

        the_soup = make_soup()
        
        totals = the_soup.find_all('div', {'class': 'Mb(10px)'})
        print("len(totals): ", len(totals))
        print(len(totals))
        # print(totals)
        # totals = soup.find_all('div.Mb(10px)')
        # #main section header._3ljve div._2W3D9 div._3FlxF div div.OxrAq
        # main.Px\(20px\) > div:nth-child(2)
        # totals = soup.find('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[3]/div/div/main/div[1]')
        for total in totals:
            # print("printing totals... ")
            # print(totals[2])
            # pattern0 captures the Total Value
            pattern0 = re.search("[$](\d+[,?]\d+\.\d+)", totals[len(totals)-1].text)
            if pattern0: values.append(pattern0.group())
                
            # pattern1 captures the Day Gain
            pattern1 = re.search("([+|-]\d+\.\d+\s\([+|-]\d+\.\d+\%\))", totals[len(totals)-1].text)
            if pattern1: values.append(pattern1.group())
            
            # pattern2 captures the Total Gain
            pattern2 = re.search("([+|-]\d+\,\d+\.\d+\s[\(][+]\d+.\d+\%\))", totals[len(totals)-1].text)
            if pattern2: values.append(pattern2.group())
    finally:
        # f.close()

        print("scraping fin.")
        # print(values)
        for key, value in zip(keys, values):
            total_values[key] = value

    print(total_values)
    return total_values


def scrape_watchlist():
    keys = ['symbol',
            'lastPrice',
            'todaysChange',
            'percentChange',
            'currency',
            'marketTime',
            'volume',
            'shares',
            'avgVol',
            'dayRange',
            'fiftyTwoWkRange',
            'dayChart',
            'marketCap'
            ]
    values = []
    watchlist_item = {}
    # watchlist = []

    filename = "watchlist.html"
    # with open(filename, 'r', encoding='utf-8') as f:
    #     contents = f.read()
    #     soup = BeautifulSoup(contents, 'lxml')
    the_soup = make_soup()
    table = the_soup.table
    try:
        # tr = table.find_all('tr')
        for tr in table.find_all('tr'):
            td = tr.find_all('td')
            if len(td) > 0:
                values = []
                for i in range(len(td)):
                    values.append(td[i].text)
                    
                for key, value in zip(keys, values):
                    watchlist_item[key] = value

                watchlist.append(watchlist_item.copy())
    finally:
        # f.close()
        print(watchlist)
        return watchlist


def write_mongo(total_values_list, watchlist_list):
    client = MongoClient(mongo_uri)
    mdb = client[mongo_dbname]
    
    totals = mdb.totals
    try:
        result = totals.insert_one(total_values_list)
        if result:
            print(str(result.inserted_id))
    except Exception as e:
        # print(str(e))
        pass
    except TimeoutException:
        pass        

    watchlist = mdb.watchlist
    try:
        for item in watchlist_list:
            resultw = watchlist.insert_one(item)
            if resultw:
                print(str(resultw.inserted_id))
    except Exception as e:
        # print(str(e))
        pass
    except TimeoutException:
        pass  


# login(driver)
# save_page(driver)
# scrape_totals(page_html)
# read_page_html()
scrape_totals()
scrape_watchlist()
write_mongo(total_values, watchlist)

# close and quit driver
driver.close()
driver.quit()
