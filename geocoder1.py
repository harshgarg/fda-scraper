import xlrd
import geocoder
import json
from xlutils.copy import copy
from streetaddress import StreetAddressFormatter, StreetAddressParser


addr_parser = StreetAddressParser()

workbook = xlrd.open_workbook("Output/MZ4/POW/output.xlsx")
sh = workbook.sheet_by_index(0)
wb = copy(workbook)
s = wb.get_sheet(0)

dict1 = {}
i=0
for n in range(sh.nrows):
  add = sh.cell_value(n,0)
  firm_name = add.split("-")
  firm_name[0] = firm_name[0] + " powai"
  print firm_name[0]
  g = geocoder.google(firm_name[0])
  s.write(n,5,str(g.latlng))
  print g.latlng
  if g.latlng != []:
    i=i+1
  dict1[add] = g.latlng

print i
wb.save("Output/MZ4/POW/output.xlsx")
f = open("result.txt","w")
json.dump(dict1,f)
f.close()

