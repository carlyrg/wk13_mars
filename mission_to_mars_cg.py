

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from splinter import Browser
import sys
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
import tweepy
from datetime import datetime
import time
import numpy as np
from config import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


def scrape():

    db = client.mars #create db "some_database"
    coll = db['news']


    #NASA news site, pull latest article text and date
    url = "https://mars.nasa.gov/api/v1/news_items/?order=publish_date+desc"
    response = requests.get(url).json()
    body = response.get('items')[0]




    url= "https://mars.nasa.gov/api/v1/news_items/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    news = requests.get(url)
    news = news.json()
    most_recent = news.get('items')[0]
    most_recent_b = most_recent['body']
    most_recent_t =most_recent['title']

    soup = BeautifulSoup(most_recent_b, 'html.parser')
    ps = soup.find_all('p')
    most_recent_body = ps[1].get_text()

    latest_news = {"title": most_recent_t, "body": most_recent_body}


    #insert into MongoDB
    #article
    coll.insert_one(latest_news)



    #MARS FEATURE IMAGE
    #soup to find image url
    img_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    image_pg = requests.get(img_url)
    soup = BeautifulSoup(image_pg.text, "html.parser")
    img_link = soup.find("a", {"class":"button fancybox"}).attrs.get('data-fancybox-href')
    # feature_image = img_url + img_link
    feature_image = f"https://www.jpl.nasa.gov{img_link}"
    
    
    #insert into MongoDB
    coll2 = db['feature_img']
    coll2.insert_one({'img':feature_image})

    # MARS WEATHER TWEET
    #twitter passcodes
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(app_key, app_secret)
    api = tweepy.API(auth)

    #pull latest 10 tweets, convert to json, read 1st tweet
    mars_tweets = []

    for status in tweepy.Cursor(api.user_timeline, id="@MarsWxReport").items(10):
        mars_tweets.append(status)

    mars_weather = mars_tweets[0]._json

    #pull text/status update of the latest tweet
    tweet_text = mars_weather['text']

    #date/time of tweet
    date = mars_weather['created_at']
    tweet_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y'))
    
    tweet = {"date": date, "tweet":tweet_text }

    # add to MongoDB
    coll3 = db['tweet']
    coll3.insert_one(tweet)
    
# MARS HEMISPHERE IMAGES
    #pull high res images from astrology site
    hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    base_hems_url= "https://astrogeology.usgs.gov"
    hems = requests.get(hemisphere_url)
    hems_soup = BeautifulSoup(hems.text, "html.parser")

    hemispheres = hems_soup.find_all("a", {"class": "product-item"})

    #empty list to hold image name/url
    mars_hemispheres=[]

    for hemi in hemispheres:
        img_title = hemi.find("h3").get_text().replace("Enhanced", "")#remove enhanced text from image title
            #remove enhanced text from image title
            # create full image url
        img_link = base_hems_url + hemi.attrs.get('href') 
            # access the downloads page for full high res image
        high_res_soup = BeautifulSoup(requests.get(img_link).text, "html.parser")
        download = high_res_soup.find("div", {"class":"downloads"})
        img_url = download.find('a')['href']
        mars_hemispheres.append({"img_title": img_title, "img_url": img_url})

    # add to MongoDB
    coll4 = db['hemisphere_images']
    coll4.insert_many(mars_hemispheres)

scrape()

# MARS FACTS
def marsFacts():
    mars_fact_url = "https://space-facts.com/mars/"

    #read html table through pandas
    mars_facts = pd.read_html(mars_fact_url)
    mars_facts_df=pd.DataFrame(mars_facts[0])

    #rename columns
    mars_facts_df.columns=["Description", "Value"]
    mars_facts_df = mars_facts_df.set_index("Description").reset_index()

    #convert table to HTML string for web
    facts_table = mars_facts_df.to_html('mars_table.html')

    return facts_table
        