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

loginUrl = os.environ.get('YAHOO_LOGIN_URL')
username = os.environ.get('YAHOO_USERNAME')
password = os.environ.get('YAHOO_PASSWORD')
watchlistUrl = os.environ.get('YAHOO_WATCHLIST_URL')

# current date and time
timeStamp = datetime.now().timestamp()
print("timestamp == ", timeStamp)
# timestamp = datetime.timestamp(now)
dt = datetime.now().strftime("%b %d, %Y @ %I:%M %p")
print("dt == ", dt)


# close and quit driver
driver.close()
driver.quit()
