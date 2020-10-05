from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

TEST_DATE = False

parse_pattern = [
    ["article.node--type-nir-news", "div.nir-widget--news--date-time", "a", "%B %d, %Y"],
    [["div.item-list", "div.wpb_wrapper"], "p:0", "a", "%b %d, %Y"],
    ["div.cell", "h5.blue", "a", "%b %d, %Y"],
    ["article.node--type-nir-news", "div.nir-widget--news--date-time", "a", "%B %d, %Y"],
    [[".newspress", "tr"], "div.nir-widget--news--date-time", "a", "%m/%d/%y"],    
    [["table.news-table", "tr"], "td.views-field-field-nir-date", "a", "%m/%d/%y"],
    [".tg-item-content-holder.tg-dark.standard-format", "span.tg-item-date", "a", "%m/%d/%y"],
    ["article.node--nir-news--nir-widget-list", "div.nir-widget--news--date-time", "a", "%B %d, %Y"],
    ["article.node--type-nir-news.node--view-mode-nir-widget-list", "div.nir-widget--news--date-time", "a", "%b %d, %Y"],
    [["div.item-list", "div.col"], ".field--name-field-nir-news-date", "a", "%m.%d.%Y"],
    ["article.node--nir-news--nir-widget-list", "div.nir-widget--news--date-time", "a", "%B %d, %Y"],
    ["article.node--nir-news--nir-widget-list", "div.nir-widget--news--date-time", "a", "%b %d, %Y"],
    [["div.group-year", "div.article"], "p.date", "a", "%B %d, %Y"],
    ["div.category-press-release", "time", "a", "%B %d, %Y"],
    ["h3.leading-normal", ".leading-tight", "a", "%Y/%m/%d", "div"],
    ["article.node--nir-news--nir-widget-list", "div.nir-widget--news--date-time", "a", "%B %d, %Y"],
    [["table.nirtable", "tr.node--nir-news--nir-widget-list"], "div.nir-widget--news--date-time", "a", "%B %d, %Y"],
    ['div.newsPub', "div.newsPub", "a", "%B %d, %Y", "div.newsDate"],
    ["article.node--nir-news--nir-widget-list", "div.nir-widget--news--date-time", "a", "%b %d, %Y"],
    ["div.news-items", "span.date", "", "%b %d, %Y"],
    ["article.media", "time", "a", "%b %d, %Y"],
    [".PressRelease", "span.PressRelease-NewsDate", "a", "%b %d, %Y %H:%M"],
]

def get_links(url, search = "press release"):
    page = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        },
    )
    
    soup = BeautifulSoup(page.text, "html.parser")
    res = []
    for link in soup.find_all('a'):
        text = link.get_text()

        if text.strip().find(search) != -1:
            res.append(link.get("href"))


    return res

def parse_section(elements, pattern):
    if (type(pattern).__name__ == 'list'):        
        for el in pattern:
            
            article_pattern = el.find(".")!= -1 and el.split(".") or [el, 0]
            if isinstance(elements, list) > 0 and len(elements) > 0:
                elements = elements[0]
            
            try:                       
                elements = elements.select(el)
            except Exception:
                elements = elements.find_all(article_pattern[0], article_pattern[1])
            
            # print(elements)
    else:        
        elements = elements.select(pattern)
        
    return elements

async def get_jshtml(session, url):
    return await session.get(url)

def parse_article_with_selenium(target, pattern, limit_date, results):
    url = target["press"]
    name = target["name"]
    source = target["url"]

    parsed_uri = urlparse(url)
    res_uri = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)


    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver.maximize_window()
    
    elements = driver
    if (name == "uniQure NV"):
        iframe = driver.find_element(By.ID, "announce")
        driver.switch_to_default_content()
        driver.switch_to.frame(iframe)
        elements = driver
    
    if (type(pattern[0]).__name__ == 'list'):        
        for el in pattern[0]:
            
            if isinstance(elements, list) > 0 and len(elements) > 0:                
                elements = elements[0]

            elements = elements.find_elements_by_css_selector(el) 

    else:        
        elements = driver.find_elements_by_css_selector(pattern[0])

    # result_file =  open(str(datetime.now())[:10] + '.csv', mode='a+', encoding='utf-8')    
    # result_writer = csv.writer(result_file, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_ALL)

    date_pattern = pattern[1].find(":") != -1 and pattern[1].split(":") or [pattern[1], 0]
    parent = False
    if (len(pattern) > 4):
        parent = True
    
    previous = False
    if pattern[0] == pattern[1]:
        parent = False
        previous = True
        prev_elements = driver.find_elements_by_css_selector(pattern[4])
    
    index = 0
    for link in elements:

        print(link.text)

        if parent:
            link = link.find_parent(pattern[4])
        
        if previous:
            div_date = prev_elements[index]
        else:            
            div_date = link.find_elements_by_css_selector(date_pattern[0])

        press_date = datetime.now()
        
        index += 1
        try:
            if isinstance(div_date, list):
                date_txt = div_date[int(date_pattern[1])].text.strip()

                for i in ["st,", "nd,", "rd,", "th,"]:
                    date_txt = date_txt.replace(i, ",")
                
                press_date = datetime.strptime(date_txt, pattern[3])
            else:
                press_date = datetime.strptime(div_date.text.strip(), pattern[3])                
            
        except:
            continue

        if not TEST_DATE and (press_date < limit_date):
            break
        # print(div_date[0].get_text())
        tag_a = link.find_elements_by_css_selector(pattern[2])
        
        for a_el in tag_a:
            press_link = a_el.get_attribute('href')
            
            if  press_link != "None" and a_el.get_attribute("href") != "#" and a_el.get_attribute("href") != "":
                title =  a_el.text.strip()
                break
        
        print_link = res_uri
        if (press_link.find(res_uri) == -1):
            print_link = print_link + press_link
        else:
            print_link = press_link
        
        results.append([name, name, title, print_link])

    driver.close()
    # result_file.close()   
    
    
def parse_article(target, pattern, limit_date,  results):
    url = target["press"]
    name = target["name"]
    source = target["url"]

    page = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        },
    )
    
    parsed_uri = urlparse(url)
    res_uri = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

    soup = BeautifulSoup(page.text, "lxml")
    
    elements = soup
    
    elements = parse_section(elements, pattern[0])
    if len(elements) == 0:
        # selenium
        parse_article_with_selenium(target, pattern, limit_date, results)
    
    # print(elements)
    # result_file =  open(str(datetime.now())[:10] + '.csv', mode='a+', encoding='utf-8')    
    # result_writer = csv.writer(result_file, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_ALL)

    
    date_pattern = pattern[1].find(":") != -1 and pattern[1].split(":") or [pattern[1], 0]
    parent = False
    if (len(pattern) > 4):
        parent = True
    
    previous = False
    if pattern[0] == pattern[1]:
        parent = False
        previous = True
    
    for link in elements:
        if parent:
            link = link.find_parent(pattern[4])
        # print(link)
        if previous:
            div_date = link.previous_element
        else:
            div_date = link.select(date_pattern[0])
        
        press_date = datetime.now()
        date_text = ""
        # print(div_date)
        try:
            if isinstance(div_date, list):
                date_txt = div_date[int(date_pattern[1])].get_text().strip()
                
                for i in ["st,", "nd,", "rd,", "th,"]:
                    date_txt = date_txt.replace(i, ",")
                
                press_date = datetime.strptime(date_txt, pattern[3])                
            else:                
                press_date = datetime.strptime(div_date.get_text().strip(), pattern[3])
        except:
            continue
        
        if not TEST_DATE and (press_date < limit_date):
            break
        # print(div_date[0].get_text())
        if (pattern[2] == ""):
            press_link = res_uri
            title = link.get_text().replace(date_text, "").strip()
            title = title[15:]
        else:
            tag_a = link.select(pattern[2])
            
            for a_el in tag_a:
                press_link = a_el.has_attr("href") and a_el.get('href') or ""
                
                if  a_el.has_attr("href") and a_el.get("href") != "#" and a_el.get("href") != "":
                    title =  a_el.get_text().strip()
                    break
        
        print_link = res_uri
        if (press_link.find(res_uri) == -1):
            print_link = print_link + press_link
        else:
            print_link = press_link
        
        results.append([name, name, title, print_link])

    # result_file.close()

def scrapeSites(targets, days):
    
    targets = [{'name': x['name'], 'url': x['url'].lower(), 'press': 'real' in x and  x['real'].lower() or ''} for x in targets]
    
    d = datetime.now() - timedelta(days=days + 1)
    i = 0
    results = []
    for target in targets:

        try:        
            if target["press"] == "":
                continue
            
            if target["name"] == "Navitor Pharmaceuticals":
                parse_article_with_selenium(target, parse_pattern[i], d, results)
            else:
                parse_article(target, parse_pattern[i], d, results)
        except:
            i += 1
            continue
        i += 1
       
        print("URL Skipped...")            
    
    return results

