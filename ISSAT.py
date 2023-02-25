from flask import Flask, render_template, request
from n2yo import n2yo
import mysql.connector
from collections import defaultdict
sat = n2yo.N2YO(api_key='your-key')
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="satellite"
)
cursor = mydb.cursor()
app = Flask(__name__)

def getsatData(satname):
    data = {}
    n1 = satname.replace("-", " ")
    n2 = satname.replace("-", "-")
    n1 = n1.replace(" ", " ")
    n2 = n2.replace(" ", "-")
    sql = "SELECT launch_date, period, launch_mass, launch_vehicle from sat as s join cat as c on s.category = c.catid where satname in ('"+n1+"', '"+n2+"');"
    cursor.execute(sql)
    res = cursor.fetchall()
    data["launch_date"] = res[0][0]
    data["period"] = res[0][1]
    data["launch_mass"] = res[0][2]
    data["launch_vehicle"] = res[0][3]
    return data


def getsatcat():
    sql = "SELECT catname, satname, nordid from sat as s join cat as c on s.category = c.catid order by catname;"
    cursor.execute(sql)
    res = cursor.fetchall()
    satcatdata = defaultdict(list)
    for row in res:
        satcatdata[row[0]].append(row[1:])
    return satcatdata

@app.route("/", methods = ['POST', 'GET'])
def index():
    noradid = request.args.get('s')
    satData = sat.get_satellite_positions(noradid, 1)
    satname = satData[0]['satname']
    data = getsatData(satname)
    data['noradid'] = noradid
    data['satname'] = satname
    data['lat'] = satData[1]['positions'][0][0]
    data['long'] = satData[1]['positions'][0][1]
    data['alt'] = satData[1]['positions'][0][2]
    satcatdata = getsatcat()
    return render_template('index.html', data=data, satcatdata=satcatdata)

@app.route("/map")
def map():
  return render_template('map.html')

if __name__ == "__main__":
    app.run(debug=True)
