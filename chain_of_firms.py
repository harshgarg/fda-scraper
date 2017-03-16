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
from collections import defaultdict

conn = psycopg2.connect(database="internstest", user="root", password="retailwhizz123", host="mdm-postgres-test.cw8vifcngblm.ap-south-1.rds.amazonaws.com", port="5432")
cur = conn.cursor()

edges = []

cur.execute("""SELECT firm_name from mdm_firm_details""")
rows = cur.fetchall()
l=0
k=0
for row in rows:

  a = row[0]
  a=a[::-1]
  #print a[::-1]

  x1 = a.split('-',1)
  x1[0] = x1[0][::-1]

  try:

    x1[1] = x1[1][::-1]
    x1[1] = row[0]
    edges.append(x1)
    l=l+1
  except:
    k=k+1
    pass

print l
print k
adj_list = defaultdict(lambda: defaultdict(lambda: 0))
i=0
for start, end in edges:
  print start + " --- " + end
  adj_list[start][end] += 1
  i=i+1

print i

for phone in adj_list:
  print phone
  for c in adj_list[phone]:
    print c

cur.execute("""SELECT id,firm_name from mdm_firm_details""")
rows = cur.fetchall()

for row in rows:
  t=0
  a = row[1]
  a=a[::-1]
  #print a[::-1]

  x1 = a.split('-',1)
  x1[0] = x1[0][::-1]

  try:
    x1[1] = x1[1][::-1]
  except:
    t=1

  if t==1:
    sql = ("""INSERT INTO mdm_chain_of_firms (firm_id,firm_name,chain,name_of_chain) VALUES (%s,%s,%s,%s)""",(row[0],row[1],"0",row[1]))
    cur.execute(*sql)
    conn.commit()
  else:
    phone_no = x1[0]
    chain_of_firms = ""
    if len(adj_list[phone_no]) == 1:
      sql = ("""INSERT INTO mdm_chain_of_firms (firm_id,firm_name,chain,name_of_chain) VALUES (%s,%s,%s,%s)""",(row[0],row[1],"0",row[1]))
      cur.execute(*sql)
      conn.commit()
    else:
      for firm_name in adj_list[phone_no]:
        chain_of_firms = chain_of_firms + firm_name + ', '


      sql = ("""INSERT INTO mdm_chain_of_firms (firm_id,firm_name,chain,name_of_chain) VALUES (%s,%s,%s,%s)""",(row[0],row[1],"1",chain_of_firms))
      cur.execute(*sql)
      conn.commit()






