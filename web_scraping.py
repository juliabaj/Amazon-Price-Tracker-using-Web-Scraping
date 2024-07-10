import requests
from bs4 import BeautifulSoup
from lxml import etree as et
import pandas as pd
from twilio.rest import Client
import sys
import time
import random
import csv
import schedule
from os import system


#Header for simulation of a real web browser when using http request to go around mechanisms that are blocking web scraping
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

#list of products to track
bucket_list = ['https://www.amazon.in/Garmin-010-02064-00-Instinct-Monitoring-Graphite/dp/B07HYX9P88/',
               'https://www.amazon.in/Rockerz-370-Headphone-Bluetooth-Lightweight/dp/B0856HRTJG/',
               'https://www.amazon.in/Logitech-MK215-Wireless-Keyboard-Mouse/dp/B012MQS060/',
               'https://www.amazon.in/Logitech-G512-Mechanical-Keyboard-Black/dp/B07BVCSRXL/',
               'https://www.amazon.in/BenQ-inch-Bezel-Monitor-Built/dp/B073NTCT4R/'
               ]

#Exctracting the price of the product from page using xpath
def get_price_of_product(dom):
    try:
        price = dom.xpath('//span[@class="a-offscreen"]/text()')[0]
        price = price.replace(',', '').replace('₹', '').replace('.00', '')
        return int(price)
    except Exception as e:
        return -1

#Extracting the name of the product from page
def get_name_of_product(dom):
    try:
        name = dom.xpath('//span[@id="productTitle"]/text()')
        name = [name.strip() for name in name]
        return name[0]
    except Exception as e:
        return -1


#Scraping the details (name, price, url) from the page
def scraping_the_data(url):
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            dom = et.HTML(str(soup))
            name = get_name_of_product(dom)
            price = get_price_of_product(dom)
            return name, price, url
        else:
            return -1, -1, url
    except Exception as e:
        return -1, -1, url

#Function to get the price of a product based on its url address, from csv file "master_list.csv"
def get_master_price(url, df):
    for row in df.itertuples():
        if row.URL == url:
            return row.Price
    return None

#Open the csv file
with open('master_list.csv', 'w', newline='', encoding='utf-8') as masterList:
    names = ['Product Name', 'Price', 'URL']
    writer = csv.DictWriter(masterList, fieldnames=names)
    writer.writeheader()

    #iterate through each url
    for url in bucket_list:
        name, price, amazon_url = scraping_the_data(url)
        writer.writerow({'Product Name': name, 'Price': price, 'URL': amazon_url})
        time.sleep(random.uniform(1, 3))
        #print(name, price)



print("Details have been saved to master_list.csv file")

#Read the csv file into a data frame
df_master = pd.read_csv('master_list.csv')

#Creating the empty lists for storing eventual price drops and their url addresses
price_drop_products = []
price_drop_url = []

#Iterate through the bucket list to check for any price drops
for product_url in bucket_list:
    #servers response to the http request contains html contents of the page
    response = requests.get(product_url, headers=header)
    #Creating a BeautifulSoup object "soup" for parsing a html content
    soup = BeautifulSoup(response.content, 'html.parser')
    #Converting a BeautifulSoup object to an lxml element
    main_dom = et.HTML(str(soup))

    current_price = get_price_of_product(main_dom)
    product_name = get_name_of_product(main_dom)


    master_price = get_master_price(product_url, df_master)

    #Checking if the current_price is lower than the master_price and if a significant price drop has been detected
    if master_price is not None and current_price < master_price:
        change_percentage = round((master_price - price)*100 / master_price)

        if change_percentage > 10:
            print(' There is a {}'.format(change_percentage), '% drop in price for {}'.format(product_name))
            print('Click here to purchase {}'. format(product_url))
            price_drop_products.append(product_name)
            price_drop_url.append(product_url)

#If there was not any significant price drop detected exit the script
if len(price_drop_products) == 0:
    sys.exit('No Price drop registered')

#Creating body of the messsage
message = 'There is a drop in price for {}'.format(len(price_drop_products)) + "products." + "Click to purchase"

for items in price_drop_products:
    message = message + "/n" + items

#Initializing informations required for sending the sms about the price drop, using Twilies
sid = 'Your SID'
token = 'Your token'

#Sending the sms
client = Client(sid, token)
message = client.messages.create(
    from_='Your Twilie number- sender of the sms',
    body=message,
    to='Number to receive sms'
)

def check_price():
    system("python3 web_scraping.py")


#Scheduling the script to run every 1 hour in order to check for any price drops
schedule.every(1).hours.do(check_price)

while True:
    schedule.run_pending()
    time.sleep(1)

