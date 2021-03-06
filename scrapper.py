from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import logging
import re
import json
import os.path


url = "http://xlnindia.gov.in/frm_G_Cold_S_Query.aspx"

driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
driver.get(url)

#all the required xpaths of the elements
state_xpath = '//*[@id="ddlState"]'
district_xpath = '//*[@id="ddldistrict"]'
taluka_xpath = '//*[@id="ddltaluka"]'
search_button_xpath = '//*[@id="btnSearch"]'
table_data_xpath = '//*[@id="dgDisplay"]/tbody/tr'
firm_name_xpath = '//*[@id="txtFirmName"]'
address_xpath = '//*[@id="txtaddress"]'

#selecting maharashtra as state
select_state = Select(driver.find_element_by_xpath(state_xpath))
select_state.select_by_value("MH")

# retrieving all the districts
select_element_district = Select(driver.find_element_by_xpath(district_xpath))

options_list_district = list(select_element_district.options)
option_values_district = map(lambda opt: opt.get_attribute('value'), options_list_district)
arr = [46]
for i in range(97,123):
  arr.append(i)
#creating output folder
currDir = "Output"

if not os.path.exists(currDir):
    os.makedirs(currDir)

#loop for all the districts
select_district = Select(driver.find_element_by_xpath(district_xpath))
for district in option_values_district:
  if district != 'MZ4':
    continue
  dis_dir = currDir
  print district

  #creating district folder
  dis_dir = dis_dir + "/" + district
  if not os.path.exists(dis_dir):
    os.makedirs(dis_dir)
  select_district = Select(driver.find_element_by_xpath(district_xpath))
  select_district.select_by_value(str(district))

  #retrieving all the talukas under the district
  select_element_taluka = Select(driver.find_element_by_xpath(taluka_xpath))

  options_list_taluka = list(select_element_taluka.options)
  option_values_taluka = map(lambda opt: opt.get_attribute('value'), options_list_taluka)

  #loop for all the talukas
  for taluka in option_values_taluka:
    if taluka != 'POW':
      continue
    if taluka == '':
      continue
    taluka_dir = dis_dir
    print "---->" + taluka

    #creating taluka folder
    taluka_dir = taluka_dir + "/" + taluka
    if not os.path.exists(taluka_dir):
      os.makedirs(taluka_dir)

    #selecting taluka
    select_taluka = Select(driver.find_element_by_xpath(taluka_xpath))
    select_taluka.select_by_value(str(taluka))

    #clicking the search button
    search = driver.find_element_by_xpath(search_button_xpath)
    search.click()

    #if number of records are more than 500 and alert is triggered
    if EC.alert_is_present()(driver):
      print "alert is present"
      alert = driver.switch_to.alert
      alert.accept()
      record_map = dict()
      records = []
      #selecting all the keywords from AA to ZZ
      for first_letter in range(97,123):
        for second_letter in arr:
          third_letter_reqd = 0
          print len(records)
          search_word = ""
          search_word = chr(first_letter) + chr(second_letter)
          firm_name = driver.find_element_by_xpath(firm_name_xpath)
          firm_name.clear()
          print search_word
          #selecting keyword from AA to ZZ and retrieving records
          firm_name.send_keys(search_word)
          search = driver.find_element_by_xpath(search_button_xpath)
          search.click()

          if EC.alert_is_present()(driver):
            print "alert detected"
            alert = driver.switch_to.alert
            alert.accept()

            for third_letter in range(97,123):
              new_search_word = ""
              new_search_word = search_word + chr(third_letter)
              firm_name = driver.find_element_by_xpath(firm_name_xpath)
              firm_name.clear()
              print new_search_word
              #selecting keyword from AA to ZZ and retrieving records
              firm_name.send_keys(new_search_word)
              search = driver.find_element_by_xpath(search_button_xpath)
              search.click()
              if EC.alert_is_present()(driver):
                print "alert detected"
                alert = driver.switch_to.alert
                alert.accept()
                continue
              rows = driver.find_elements_by_xpath(table_data_xpath)


          #getting license number on mousehover
              for row in rows:
               # Skip headers row
                if row.get_attribute("onmouseover") is None:
                  continue


                parsed_row = BeautifulSoup(row.get_attribute("outerHTML"), "html.parser")
                mouseover = parsed_row.tr.attrs['onmouseover']
                tooltip = re.findall(r"Tip\(\'(.*?)\'\)", mouseover)[0].strip()
                if tooltip.startswith("<span"):
                  tt_element = BeautifulSoup(tooltip, "html.parser")
                  tooltip = map(str,
                  filter(lambda elem: elem != BeautifulSoup("<br/>", "html.parser").br,
                  tt_element.span.contents))

                #putting all the data in record variable
                record = {
                  "firm_name": row.find_element_by_xpath(".//td[1]").text,
                  "address": row.find_element_by_xpath(".//td[2]").text,
                  "licenses": row.find_element_by_xpath(".//td[3]").text,
                  "reg_pharma_comp_person": row.find_element_by_xpath(".//td[4]").text,
                  "tooltip": tooltip,
                  }

                #checking for duplicates and avoiding them
                firm_name_hash = row.find_element_by_xpath(".//td[1]").text
                if firm_name_hash in record_map:
                  #print "duplicate " + firm_name_hash
                  continue
                else:
                  record_map[firm_name_hash] = '1'
                  #print firm_name_hash
                  records.append(record)

          else:
            rows = driver.find_elements_by_xpath(table_data_xpath)


            #getting license number on mousehover
            for row in rows:
             # Skip headers row
              if row.get_attribute("onmouseover") is None:
                continue


              parsed_row = BeautifulSoup(row.get_attribute("outerHTML"), "html.parser")
              mouseover = parsed_row.tr.attrs['onmouseover']
              tooltip = re.findall(r"Tip\(\'(.*?)\'\)", mouseover)[0].strip()
              if tooltip.startswith("<span"):
                tt_element = BeautifulSoup(tooltip, "html.parser")
                tooltip = map(str,
                filter(lambda elem: elem != BeautifulSoup("<br/>", "html.parser").br,
                tt_element.span.contents))

              #putting all the data in record variable
              record = {
                "firm_name": row.find_element_by_xpath(".//td[1]").text,
                "address": row.find_element_by_xpath(".//td[2]").text,
                "licenses": row.find_element_by_xpath(".//td[3]").text,
                "reg_pharma_comp_person": row.find_element_by_xpath(".//td[4]").text,
                "tooltip": tooltip,
                }

              #checking for duplicates and avoiding them
              firm_name_hash = row.find_element_by_xpath(".//td[1]").text
              if firm_name_hash in record_map:
                #print "duplicate " + firm_name_hash
                continue
              else:
                record_map[firm_name_hash] = '1'
                #print firm_name_hash
                records.append(record)




    #if alert is not present directly retrieve the records
    else:
      print "no alert"
      rows = driver.find_elements_by_xpath(table_data_xpath)
      records = []
      #retrieving all the records and licence number on hover
      for row in rows:
        # Skip headers row
        if row.get_attribute("onmouseover") is None:
          continue


        parsed_row = BeautifulSoup(row.get_attribute("outerHTML"), "html.parser")
        mouseover = parsed_row.tr.attrs['onmouseover']
        tooltip = re.findall(r"Tip\(\'(.*?)\'\)", mouseover)[0].strip()
        if tooltip.startswith("<span"):
          tt_element = BeautifulSoup(tooltip, "html.parser")
          tooltip = map(str,
          filter(lambda elem: elem != BeautifulSoup("<br/>", "html.parser").br,
          tt_element.span.contents))

        #putting data in record variable
        record = {
          "firm_name": row.find_element_by_xpath(".//td[1]").text,
          "address": row.find_element_by_xpath(".//td[2]").text,
          "licenses": row.find_element_by_xpath(".//td[3]").text,
          "reg_pharma_comp_person": row.find_element_by_xpath(".//td[4]").text,
          "tooltip": tooltip,
          }

        records.append(record)
    #creating output file and saving data is json format
    f= open(taluka_dir + "/output.txt","w")
    json.dump(records, f)
    f.close()
    f= open(taluka_dir + "/output.txt","a")
    f.write(str(len(records)))
    f.close()




