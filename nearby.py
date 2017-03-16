from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import logging
import re
import json
import os.path
import csv
import tablib
import geocoder
import psycopg2
import urllib2
import requests

json_resp = json.load(urllib2.urlopen('https://maps.googleapis.com/maps/api/place/radarsearch/json?location=19.122929,%2072.91884499999999&radius=5000&rankBy=distance&type=doctors&key=AIzaSyApU_wWYwjI-fXnO4vQs0PNXgX7gnFUwH8'))
#print json_resp['results']

for item in json_resp['results']:
  item_place_id = item['place_id']
  urlx =  'https://maps.googleapis.com/maps/api/place/details/json?placeid='+item_place_id+'&key=AIzaSyApU_wWYwjI-fXnO4vQs0PNXgX7gnFUwH8'
  place_resp = json.load(urllib2.urlopen(urlx))
  print place_resp['result']['name'] + " " + place_resp['result']['vicinity']

