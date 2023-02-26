from flask import Flask, render_template, request, redirect
from n2yo import n2yo
import mysql.connector
import folium
import math
import wikipedia
from collections import defaultdict
sat = n2yo.N2YO(api_key='your_key')
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
    sql = "SELECT launch_date, period, launch_mass, launch_vehicle from sat as s left outer join cat as c on s.category = c.catid where satname in ('"+n1+"', '"+n2+"');"
    cursor.execute(sql)
    res = cursor.fetchall()
    data["launch_date"] = res[0][0]
    data["period"] = res[0][1]
    data["launch_mass"] = res[0][2]
    data["launch_vehicle"] = res[0][3]
    return data

def getLatest():
    sql = "SELECT nordid from sat LIMIT 1;"
    cursor.execute(sql)
    res = cursor.fetchall()
    return res[0][0]

def getsatcat():
    sql = "SELECT catname, satname, nordid from sat as s join cat as c on s.category = c.catid order by catname;"
    cursor.execute(sql)
    res = cursor.fetchall()
    satcatdata = defaultdict(list)
    for row in res:
        satcatdata[row[0]].append(row[1:])
    return satcatdata

def PlotTrajectory(noradid):
    my_map = folium.Map(zoom_start=16, width=900,height=500, tiles="cartodbdark_matter")
    data = sat.get_satellite_positions(noradid, 3600)
    data = data[1]['positions']
    cord = []
    for i in range(0, len(data), 10):
        if math.floor(data[i][1]) in [179, 178, -179, -178]:
            break
        cord.append([data[i][0], data[i][1]])


    folium.PolyLine(cord, color="green", weight=2.5, opacity=1).add_to(my_map)
    pushpin = folium.features.CustomIcon('static/img/marker.png', icon_size=(30,30))
    folium.Marker(location = [data[0][0], data[0][1]], icon=pushpin).add_to(my_map)
    my_map.save("templates/map.html")

@app.route("/", methods = ['POST', 'GET'])
def index():
    if request.args.get('s'):
        noradid = request.args.get('s')
    else:
        noradid = getLatest()
        return redirect("?s="+str(noradid))
    satData = sat.get_satellite_positions(noradid, 1)
    satname = satData[0]['satname']
    data = getsatData(satname)
    data['noradid'] = noradid
    data['satname'] = satname
    data['lat'] = satData[1]['positions'][0][0]
    data['long'] = satData[1]['positions'][0][1]
    data['alt'] = satData[1]['positions'][0][2]
    data['summary'] = wikipedia.summary(satname)
    satcatdata = getsatcat()
    PlotTrajectory(noradid)
    return render_template('index.html', data=data, satcatdata=satcatdata)


@app.route("/map")
def map():
    return render_template('map.html')

if __name__ == "__main__":
    app.run(debug=True)
