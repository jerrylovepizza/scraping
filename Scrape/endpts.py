from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import urllib
from time import sleep
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def eparse_page(targets, pagenum, d, results, driver):

    if (pagenum > d):
        return False

    condition = "Last week"
    if (d > 7):
        condition = "4 months ago"
    
    sources = "https://www.endpts.com/news/page/"
    p_sources = sources + str(pagenum)
    
    driver.get(p_sources)
    
    elements = driver.find_elements_by_css_selector(".epn_white_box")
    
    for article in elements:
        try:
            a_links = article.find_elements_by_tag_name("a")   
            if not isinstance(a_links, list) or len(a_links) == 0:
                return True
            a_link = a_links[0]
            title = a_link.get_attribute("title").strip()
            link = a_link.get_attribute("href")
            time = article.find_elements_by_css_selector(".epn_time")        
            time = time[0].text.strip()
            
            if time.find(condition) == -1: #Last week
                
                small_title = title.lower().replace("-", "")
                # results.append([small_title, "endpts", title, link])
                for t in targets:
                    # print(title)
                    # print(small_title.find(t["name"].lower()))
                    if (small_title.find(t["name"].lower()) != -1):
                        results.append([t["name"], t["name"], title, link])
                        break
            else:
                return False
            
        except Exception:
            continue
    
    return True
   

def endpts(targets, days):
    targets = [{'name': x['name'], 'url': x['url'].lower()} for x in targets]
    results = []

    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    # driver_url = driver_path    
    # driver = webdriver.Chrome(executable_path=driver_url, chrome_options=chrome_options)
    # driver.maximize_window()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver.maximize_window()

    d = datetime.now() - timedelta(days=days + 1)
    pagenum = 0
    res = True

    # for t in targets:
    pagenum = 1
    res = True

    try:
        while (res):
            res = eparse_page(targets, pagenum, days, results, driver)
            pagenum += 1
            sleep(2)
    except Exception as e:
        print (e)
    
    driver.close()
    return results

