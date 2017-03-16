from bs4 import BeautifulSoup
from selenium import webdriver
import selenium.webdriver.support.ui as UI
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

url = "http://xlnindia.gov.in/frm_G_Cold_S_Query.aspx"

driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
driver.get(url)

state_xpath = '//*[@id="ddlState"]'
district_xpath = '//*[@id="ddldistrict"]'
taluka_xpath = '//*[@id="ddltaluka"]'
search_button_xpath = '//*[@id="btnSearch"]'
table_data_xpath = '//*[@id="dgDisplay"]/tbody/tr'
firm_name_xpath = '//*[@id="txtFirmName"]'
address_xpath = '//*[@id="txtaddress"]'

with open('output.xlsx', 'wb') as xlfile:
  book = tablib.Databook()
  headers = ["State Name", "State Code", "District Name","District Code","Taluka Name","Taluka Code"]
  sheet = tablib.Dataset(headers=headers)

  select_state = UI.Select(driver.find_element_by_xpath(state_xpath))

  #options_list_state = list(select_state.options)
  #option_values_state = map(lambda opt: opt.get_attribute('text'), options_list_state)


  options_list_state = list(select_state.options)
  option_values_state_text = map(lambda opt: opt.get_attribute('text'), options_list_state)
  options_list_state = list(select_state.options)
  option_values_state_value = map(lambda opt: opt.get_attribute('value'), options_list_state)
  state_map={}
  iter_state= 0
  for state in option_values_state_text:
    state_map[str(option_values_state_text[iter_state])] = str(option_values_state_value[iter_state])
    iter_state = iter_state + 1

  print state_map

  for state in option_values_state_text:
    select_state = Select(driver.find_element_by_xpath(state_xpath))
    select_state.select_by_visible_text(str(state))

    # retrieving all the districts
    select_element_district = Select(driver.find_element_by_xpath(district_xpath))

    options_list_district = list(select_element_district.options)
    option_values_district_text = map(lambda opt: opt.get_attribute('text'), options_list_district)
    options_list_district = list(select_element_district.options)
    option_values_district_value = map(lambda opt: opt.get_attribute('value'), options_list_district)
    district_map={}
    iter_district=0
    for district in option_values_district_text:

      district_map[str(option_values_district_text[iter_district])] = str(option_values_district_value[iter_district])
      iter_district = iter_district + 1

    for district in option_values_district_text:
      if str(district) == "--Select--" or str(district) == "":
        continue
      select_district = Select(driver.find_element_by_xpath(district_xpath))
      select_district.select_by_visible_text(str(district))

      select_taluka = Select(driver.find_element_by_xpath(taluka_xpath))

      for taluka in select_taluka.options:
        if str(taluka.text) == "--Select--" or str(taluka.text) == "":
          continue
        sheet.append([state,state_map[str(state)],str(district),district_map[str(district)],str(taluka.text),taluka.get_attribute('value')])
        print state + " " + state_map[str(state)] + " " + str(district) + " " + district_map[str(district)] + " " + str(taluka.text) + " " + taluka.get_attribute('value')

  book.add_sheet(sheet)
  xlfile.write(book.xlsx)
