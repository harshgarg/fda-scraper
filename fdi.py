#! $(which python)

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import logging
import re
import json
import os.path


def setup_console_logging():
    # Setup logging
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(name)s|%(funcName)s:%(lineno)d - %(message)s")
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log


log = setup_console_logging()

SINGLE_STATE = "maharashtra"
SINGLE_STATE_SHORT_CODE = "MH"
DISTRICTS_OPTIONS = []


class FDAScraper(object):
    def __init__(self):
        self.start_url = "http://xlnindia.gov.in/frm_G_Cold_S_Query.aspx"

        self.state_xpath = '//*[@id="ddlState"]'
        # state_sc_xpath = '//*[@id="ddlState"]/option/@value'
        self.district_xpath = '//*[@id="ddldistrict"]'
        # district_scode_xpath = '//*[@id="ddldistrict"]/option/@value'
        self.taluk_xpath = '//*[@id="ddltaluka"]'
        # taluk_scode_xpath = '//*[@id="ddltaluka"]/option/@value'
        self.category_xpath = '//*[@id="ddlCategory"]'

        self.search_button_xpath = '//*[@id="btnSearch"]'
        self.retailer_rows_xpath = '//*[@id="dgDisplay"]/tbody/tr'
        self.number_of_rows_xpath = '//*[@id="lbnoofrows"]'

    def extract_retailer(self, driver):
        pass

    def iterate_over_select_options(self, driver, xpath_string):
        # Create select element over DOM object
        select_element = Select(driver.find_element_by_xpath(xpath_string))

        options_list = list(select_element.options)
        option_values = map(lambda opt: opt.get_attribute('value'), options_list)

        # Force Mumbai-Zone 1-7 Districts
        log.debug("BEFORE setup...")
        if self.get_current_state(driver).lower() == SINGLE_STATE and xpath_string.find("ddldistrict") > 0:
            log.debug("Setting up district subset...")

            # Overriding option_values
            if DISTRICTS_OPTIONS:
                option_values = DISTRICTS_OPTIONS

        # Iterate over the Options
        for opt_val in option_values:
            if not opt_val:
                # log.debug("Skipping OptVal: {}".format(opt_val))
                continue
            select_element = Select(driver.find_element_by_xpath(xpath_string))

            # log.debug("Selecting OptVal: {}".format(opt_val))
            select_element.select_by_value(opt_val)
            yield select_element

    def get_selected_option(self, driver, parent_xpath):
        # Create select element over DOM object
        select_element = Select(driver.find_element_by_xpath(parent_xpath))
        return select_element.first_selected_option

    def get_current_state(self, driver):
        state_elem = self.get_selected_option(driver, self.state_xpath)
        return state_elem.text.strip() if state_elem.text.strip() else state_elem.get_attribute("value")

    def get_current_district(self, driver):
        district = self.get_selected_option(driver, self.district_xpath)
        return district.text.strip() if district.text.strip() else district.get_attribute("value")

    def get_current_taluk(self, driver):
        taluk = self.get_selected_option(driver, self.taluk_xpath)
        return taluk.text.strip() if taluk.text.strip() else taluk.get_attribute("value")

    def start(self, url):
        try:
            # Create an instance of browser and load FDA page
            driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
            driver.get(url)

            # Iterate over the states and select Districts
            for state_select in self.iterate_over_select_options(driver, self.state_xpath):

                # Force Single selection
                select_element = Select(driver.find_element_by_xpath(self.state_xpath))
                select_element.select_by_value(SINGLE_STATE_SHORT_CODE)

                # retailers = {self.get_current_state(driver): {}}
                for district_select in self.iterate_over_select_options(driver, self.district_xpath):

                    # Auto-Skip Rule
                    # if the file exists in output path, then dont scrape data for it
                    state = self.get_current_state(driver)
                    district = self.get_current_district(driver)
                    scraped_file = os.path.join(os.path.abspath(os.curdir),
                                                "output",
                                                "{}.{}.json".format(state, district))
                    if os.path.exists(scraped_file):
                        log.info("Skipping {}.{}".format(state, district))
                        continue

                    retailers = {
                        self.get_current_state(driver): {
                            self.get_current_district(driver): {}
                        }
                    }
                    i = 0;
                    # retailers[self.get_current_state(driver)][self.get_current_district(driver)] = {}
                    for taluk_select in self.iterate_over_select_options(driver, self.taluk_xpath):
                        i = i + 1
                        if i == 4:
                            break
                        state = self.get_current_state(driver)
                        district = self.get_current_district(driver)
                        taluk = self.get_current_taluk(driver)

                        # Now do search
                        search = driver.find_element_by_xpath(self.search_button_xpath)
                        search.click()

                        if EC.alert_is_present()(driver):
                            log.error(
                                "Encountered Alert for 500+ records. Location: {}:{}:{}".format(state, district, taluk))
                            alert = driver.switch_to.alert
                            alert.accept()
                            continue

                        records = []

                        try:
                            num_of_records = driver.find_element_by_xpath(self.number_of_rows_xpath).text

                            # Check for table '//*[@id="dgDisplay"]' to validate presence of rows
                            rows = driver.find_elements_by_xpath(self.retailer_rows_xpath)

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

                                record = {
                                    "firm_name": row.find_element_by_xpath(".//td[1]").text,
                                    "address": row.find_element_by_xpath(".//td[2]").text,
                                    "licenses": row.find_element_by_xpath(".//td[3]").text,
                                    "reg_pharma_comp_person": row.find_element_by_xpath(".//td[4]").text,
                                    "tooltip": tooltip,
                                }

                                records.append(record)

                        except NoSuchElementException:
                            num_of_records = 0

                        # Create record
                        retailers[self.get_current_state(driver)][self.get_current_district(driver)][self.get_current_taluk(driver)] = records

                        log.debug("{}:{}:{} -> {}".format(state, district, taluk, num_of_records))

                    # Write contents to file
                    print "this is executing1"
                    with open("output/{}.{}.json".format(self.get_current_state(driver), self.get_current_district(driver)), "w") as state_file:
                        state_file.write(json.dumps(retailers, indent=2))

                break

        except KeyboardInterrupt:
            log.warn("Detected 'Ctrl+C'.Terminating on User Request...")

        except Exception:
            log.exception("Unknown Error. {}".format(locals()))

        finally:
            driver.close()


if __name__ == '__main__':
    FDAScraper().start(url="http://xlnindia.gov.in/frm_G_Cold_S_Query.aspx")
