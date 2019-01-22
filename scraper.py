#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import os

driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10) # seconds

loginUrl = os.environ.get('YAHOO_LOGIN_URL')
username = os.environ.get('YAHOO_USERNAME')
password = os.environ.get('YAHOO_PASSWORD')
watchlistUrl = os.environ.get('YAHOO_WATCHLIST_URL')

# current date and time
timeStamp = datetime.now().timestamp()
print("timestamp == ", timeStamp)
dt = datetime.now().strftime("%b %d, %Y @ %I:%M %p")
print("dt == ", dt)

# login to get handle on driver
def login(driver):

    try:
        print(loginUrl)
        driver.get(loginUrl)
    
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
       
        print(watchlistUrl)
        # elem = wait.until(EC.title_contains(driver.title))
        # print(driver.title)
        driver.get(watchlistUrl)

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

login(driver)
# close and quit driver
driver.close()
driver.quit()
