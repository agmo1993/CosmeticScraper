from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import csv
import datetime
import os
import time
import re
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_pandas import Spread


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']



credentials = ServiceAccountCredentials.from_json_keyfile_name('My Project 53889-05501a7fa707.json', scope)

gc = gspread.authorize(credentials)


class Scraper:
    
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(executable_path=r'C:/Users/Abdul Rehman/Downloads/geckodriver-v0.26.0-win64/geckodriver.exe')
        #self.driver.get("https://www.lookfantastic.com/")
        self.spreadsheet_key = Spread("https://docs.google.com/spreadsheets/d/1aradT8_30SUbEj13ZyDju78V80eJB-rJyX9UmJGBxHA/edit?usp=sharing")
        now = datetime.datetime.now()
        self.date = now.strftime("%Y.%m.%d")
        self.data = pd.DataFrame(columns=['Brand','Title','Price(EUR)','Review','Url'])
        #self.f = open("cometic_test" + self.date + ".csv","w", encoding='utf8')
        #button = self.driver.find_element_by_xpath('//*[@class="emailReengagement_close_button"]')
        #button.click()
        self.urls = {
            "https://www.lookfantastic.com/health-beauty/fragrance/eau-de-toilette.list" : "Eau de toilette",
            "https://www.lookfantastic.com/health-beauty/fragrance/eau-de-parfum.list" : "Eau de Parfum",
            "https://www.lookfantastic.com/brands/mac/view-all.list" : "MAC"            
        }

    """
    def sendQuery(self, queryList):
        query = ""
        for i in queryList:
            query += i
        self.driver.find_element_by_id("simpleSearchForm:fpSearch:input").send_keys(query)
        self.driver.find_element_by_id("simpleSearchForm:fpSearch:buttons").click()
        return True
    """

    def formatResultsPage(self):
        select_relevance = Select(self.driver.find_element_by_css_selector('select.ps-plain-select--input '))
        select_relevance.select_by_index(1)
        
        """
        select_max_results = Select(self.driver.find_element_by_id("resultListCommandsForm:perPage:input"))
        select_max_results.select_by_value("200")
        """
        """
        ------------------FIX ABOVE TO GET 200 RESULTS PER PAGE---------------------
        """
        #self.driver.refresh()
        return True

    def collectResults(self, category):

        soup = BeautifulSoup(self.driver.page_source,'lxml')
        table = soup.findAll("span",{ "class" : ["js-enhanced-ecommerce-data hidden"]})
        reviews = soup.findAll("span", {"class" : "productBlock_ratingValue"})
        urls = soup.findAll("a", {"class" : "productBlock_link"})
        counter = 0
        for i in table:
            new_row = {}
            product_brand = i["data-product-brand"]
            new_row['Brand'] = product_brand
            product_title = i["data-product-title"]
            url = urls[counter]
            url = url["href"]
            if "Various Sizes" in product_title:
                print("Various sizes available")
                self.driver.get("https://www.lookfantastic.com"+url)
                time.sleep(3)


            new_row['Title'] = product_title
            product_price = i["data-product-price"]
            if len(re.findall('\d*\.?\d+,\d*\.?\d+',product_price)) >= 1:
                product_price = re.findall('\d*\.?\d+,\d*\.?\d+',product_price)[0]
                product_price = product_price.replace(",", "")
                
            else:
                product_price = re.findall('\d*\.?\d+',product_price)[0]

            new_row['Price(EUR)'] = product_price
            review = reviews[counter].text
            new_row['Review'] = review

            
            new_row['Url'] = url
            new_row['Category'] = category
            new_row['Price_Date'] = self.date
            self.data = self.data.append(new_row, ignore_index=True)
            #self.f.write(product_brand + "," + product_title + "," + product_price + "," + review + "," + "\n")

        
        
        #self.keepCrawling()

        #self.driver.close()

    def keepCrawling(self):

        #self.collectResults()
        
        for page_url in self.urls:

            page_counter = 0
            while True:
                
                url = page_url + "?pageNumber=" + str(page_counter) + "&switchcurrency=EUR"
                self.driver.get(url)
                soup = BeautifulSoup(self.driver.page_source,'lxml')
                h1 = soup.findAll("p",{ "class" : ["responsiveProductListHeader_resultsCount"]})
                
                if h1[0].text == None:
                    break
                
                print("Scraping: " + self.urls[page_url] + " page " + str(page_counter))

                try:
                    time.sleep(3)
                    self.collectResults(self.urls[page_url])
                    page_counter += 1
                except Exception as e:
                    print(str(e))
                    break
        
        
        self.spreadsheet_key.df_to_sheet(self.data, index=False, sheet=(self.date))

        #self.driver.close()

        #self.f.close()
        
        #self.driver.refresh()

        
        #self.collectResults()
    def testSoup(self):
        self.driver.get("https://www.lookfantastic.com/yves-saint-laurent-libre-eau-de-parfum-various-sizes/12218719.html")
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        close_popup = self.driver.find_element_by_class_name("close-button")
        close_popup.click()
        close_cookie = self.driver.find_element_by_class_name("cookie_modal_button")
        close_cookie.click()
        various_sizes = soup.findAll("div",{"class":"productVariations_boxes"})
        text = str(various_sizes[0])
        print(text)
        labels_soup = BeautifulSoup(text)
        labels = labels_soup.findAll("button")
        print(labels)

        for i in labels:
            size = i["data-option-id"]
            print(size)
            button = self.driver.find_element_by_xpath("//button[@data-option-id=" + "'" + str(size)+ "']")
            button.click()
            time.sleep(3)
            price_soup = BeautifulSoup(self.driver.page_source,'lxml')
            price = price_soup.findAll("p",{"class":"productPrice_price"})
            print(price)

    






        

cosmetic_scraper = Scraper()
#cannabis_scraper.formatResultsPage()
#cannabis_scraper.collectResults()
cosmetic_scraper.testSoup()


