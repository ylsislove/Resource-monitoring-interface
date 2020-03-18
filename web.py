#!/usr/bin/env python
#coding=utf-8
import MySQLdb as mysql
import json
from flask import Flask, request, render_template
app = Flask(__name__)

db = mysql.connect(user='root', passwd='root123456',
                   db='falcon', charset='utf8')
db.autocommit(True)
c = db.cursor()

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/data', methods=['GET'])
def getData():
    c.execute('select time, mem_usage, cpu_percent, network_sent, network_recv from (select * from stat order by time desc limit 300) temp order by time')
    data = c.fetchall()
    mem = [{'time':i[0]*1000, 'value':i[1]} for i in data]
    cpu = [{'time':i[0]*1000, 'value':i[2]} for i in data]
    netinfo = []
    for i in data:
        netinfo.append({'time':i[0]*1000, 'value':i[3]/1000, 'type':'send'})
        netinfo.append({'time':i[0]*1000, 'value':i[4]/1000, 'type':'recv'})
    # print(top[0])
    return json.dumps({'mem':mem, 'cpu':cpu, 'netinfo':netinfo})

app.run(port=5000, debug=True)
