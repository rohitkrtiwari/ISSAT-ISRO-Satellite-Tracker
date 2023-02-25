import requests as re
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="satellite"
)
mycursor = mydb.cursor()

r = re.get('https://www.n2yo.com/satellites/?c=IND&t=country')

soup = BeautifulSoup(r.text, features="lxml")

table = soup.find('table', class_='footable countrytab')

df = pd.DataFrame(columns=['NORAD ID', 'Name', 'Launch Date', 'Period'])
for row in table.find_all('tr'):    
    columns = row.find_all('td')
    if(columns != []):
        name = columns[0].text.strip()
        norad_ID = columns[1].text.strip()
        LaunchDate = columns[3].text
        Period = columns[4].text
        df = df.append({'NORAD ID': norad_ID, 'Name': name,  'Launch Date': LaunchDate, 'Period': Period}, ignore_index=True)

sql = "INSERT INTO `sat` (`nordid`, `satname`, `launch_date`, `period`) VALUES (%s, %s, %s, %s)"

l = (df['NORAD ID'] + "\t" + df['Name'] + "\t" + df['Launch Date'] + "\t" + df['Period']).to_list()

for i in range(len(l)):
    l[i] = list(l[i].split("\t"))

for i in (l):
    print(sql, (i[0], i[1], i[2], i[3]))
    mycursor.execute(sql, (i[0], i[1], i[2], i[3]))
    mydb.commit()

