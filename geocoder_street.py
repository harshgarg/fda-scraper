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

def get_geocode(add):
  print add
  g = geocoder.google(add)
  print g.latlng

# conn = psycopg2.connect(database="internstest", user="root", password="retailwhizz123", host="mdm-postgres-test.cw8vifcngblm.ap-south-1.rds.amazonaws.com", port="5432")
# cur = conn.cursor()

# cur.execute("""SELECT * from mdm_firm_details""")
# rows = cur.fetchall()
with open('mdm_firm_details.csv') as csvfile:
  rows = csv.DictReader(csvfile)

  for row in rows:
    geocode = row['geocode']
    taluka = row['taluka']
    city = row['city']
    if geocode == "{}":
      #print "not found"
      address = row['address']
      address = address[::-1]
      if address[0] == ',':
        address = address[1:]
      #print address
      address = address.split(",",1)
      #print address[0]
      address_x = address[1].split(",",1)
      address_2 = address_x[0]
      address_1 = address[0]
      address_1 = address_1[::-1].lower()
      address_2 = address_2[::-1].lower()

      taluka = taluka.split(' ',1)
      taluka_name = taluka[0]
      taluka_name = taluka_name.split('-',1)
      city = city.split(' ',1)
      city_name = city[0]
      city_name = city_name.split('-',1)
      taluka_name[0] = taluka_name[0].replace(' ','').lower()

      city_name[0] = city_name[0].replace(' ','').lower()
      if taluka_name[0] == address_1.replace(' ',''):
        if city_name[0] == taluka_name[0]:
          get_geocode(address_2 + " " + city_name[0])
        else:
          get_geocode(address_2 + " " + address_1 + " " + city_name[0])
      else:
        get_geocode(address_1 + " " + city_name[0])

    else:
      print geocode

