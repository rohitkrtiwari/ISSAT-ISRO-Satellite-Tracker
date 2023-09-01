import requests as re
from bs4 import BeautifulSoup
import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="satellite"
)
mycursor = mydb.cursor()
r = re.get('https://www.isro.gov.in/Student_Satellite.html')
soup = BeautifulSoup(r.text)
table = soup.find('tbody', class_='list')
for row in table.find_all('tr'):    
    columns = row.find_all('td')
    name = columns[1].text.strip()
    launch_mass = columns[3].text.strip()
    launch_vehicle = columns[4].text.strip()
    launch_vehicle = launch_vehicle.replace("\n"," ")
    launch_vehicle = " ".join(launch_vehicle.split())
    n1 = name.replace("-", " ")
    n2 = name.replace("-", "-")
    n1 = n1.replace(" ", " ")
    n2 = n2.replace(" ", "-")

    sql = "UPDATE `sat` set launch_mass = '" + launch_mass+ "', launch_vehicle = '" + launch_vehicle+ "' WHERE satname IN ('"+n1+"', '"+n2+"');"
    print(sql)
    mycursor.execute(sql)
    mydb.commit()
    # break
