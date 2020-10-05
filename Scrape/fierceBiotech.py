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
from selenium.common.exceptions import NoSuchElementException

def parse_page(targets, pagenum, d, results, source, driver):
    
    if pagenum > 40:
        return False

    p_sources = source + str(pagenum)
    driver.get(p_sources)   
    sleep(10)
    elements = driver.find_elements_by_css_selector("div.article")

    # page = requests.get(p_sources)
    # soup = BeautifulSoup(page.text, "lxml")

    # elements = soup.find_all("article", {"class": "card"})
    # print(elements)
    
    for article in elements:
        
        h2s = article.find_elements_by_css_selector("h2.list-title")
        if len(h2s) == 0:
            continue
        title = h2s[0].text.strip()
        
        try:
            link = h2s[0].find_element_by_tag_name("a").get_attribute("href")
            time =  article.find_element_by_tag_name("time").text.strip()            
            post_date = datetime.strptime(time, "%b %d, %Y, %H:%M %p")
            
            if post_date > d:
                # results.append(["12", "fiercebiotech", title, link])
                small_title = title.lower()

                for t in targets:
                    if (small_title.find(t["name"].lower()) != -1):
                        results.append([t["name"], t["name"], title, link])
                        break
            else:
                return False
        except NoSuchElementException:
            continue
    return True
   

def fierceBioTech(targets, days):
    targets = [{'name': x['name'], 'url': x['url'].lower()} for x in targets]
    results = []
    sources = [
        "https://www.fiercebiotech.com/biotech?page=",
        "https://www.fiercebiotech.com/medtech?page=",
        "https://www.fiercebiotech.com/cro?page=",        
        "https://www.fiercebiotech.com/research?page="
    ]
    d = datetime.now() - timedelta(days=days + 1)
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver.maximize_window()

    i = 0
    for source in sources:
        pagenum = 1
        res = True
        
        while (res):
            res = parse_page(targets, pagenum, d, results, source, driver)
            pagenum += 1

    driver.close()

    return results
