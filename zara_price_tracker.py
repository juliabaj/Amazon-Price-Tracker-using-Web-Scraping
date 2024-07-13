import requests
from bs4 import BeautifulSoup
from lxml import etree as et
from lxml import html
import pandas as pd
from twilio.rest import Client
import sys
import time
from time import sleep
import random
import csv
import schedule
from os import system
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

link_of_the_item = input("Put here the link to the item you want to track: ")

chrome_driver_path = r"C:\Users\Dell\Downloads\chromedriver_win64\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver_service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

driver.get(link_of_the_item)
driver.maximize_window()

height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    sleep(5)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if height == new_height:
        break

    height = new_height

page_product_links = driver.find_elements(By.XPATH, '//div[@class="product-grid-product__figure"]/a')

# Getting the product links
for product in page_product_links:
    product_link = product.get_attribute('href')
def get_price(dom):
    try:
        price = driver.find_element(By.XPATH, '//span[@class="money-amount__main"]').text
        price = float(price.replace(',', '').replace('PLN', '').strip())
        return price
    except Exception as e:
        print("Failed")
        return -1


def get_name(dom):
    try:
        name = driver.find_element(By.XPATH,'//h1[@class="product-detail-info__header-name"]').text
        return name.strip()
        print(name)
    except Exception as e:
        print("Failed")
        return -1

def extract_info(url):
    try:
        response = requests.get(url, headers=header)
        # check for http requests errors
        response.raise_for_status()
        dom = html.fromstring(response.content)

        price = get_price(dom)
        name = get_name(dom)

        if price is not None and name is not None:
            print(f"Product's name: {name}")
            print(f"Product's price: {price}")

        else:
            print("Failed to extract product's informations")
    except requests.exceptions.RequestException as e:
            print(f"HTTP request failed: {e}")


extract_info(link_of_the_item)


