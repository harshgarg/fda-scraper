import xlrd
import geocoder
import json
from streetaddress import StreetAddressFormatter, StreetAddressParser

addr_parser = StreetAddressParser()

workbook = xlrd.open_workbook("output.xlsx")
sh = workbook.sheet_by_index(0)

dict1 = {}

for n in range(sh.nrows):
  add = sh.cell_value(n,0)
  firm_name = add.split("-")
  firm_name = firm_name + " powai"
  g = geocoder.google(firm_name)
  print g.latlng
  dict1[add] = g.latlng


f = open("result.txt","w")
json.dump(dict1,f)
f.close()

