#!/usr/bin/env python
# coding: utf-8

from urllib import request
import urllib
import urllib.request
import socket
import os
import base64
from io import BytesIO
import sys
from flask import Flask
from flask import render_template
from redis import Redis, RedisError
import requests
import json
import uuid
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import time

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

@app.route("/")
def hello():
    url = 'http://10.0.2.2:8083/moveIns'
    url2 = 'http://10.0.2.2:8083/leadToMoveInTimes'

    response = urllib.request.urlopen(url)
    response2 = urllib.request.urlopen(url2)

    data = json.load(response)
    data2 = json.load(response2)

    response.close()
    response2.close()

    present = datetime.now()

    moveInList = []
    leadMoveInList = []

    for mi in data:
        moveIns = {}
        datetime_object = datetime.strptime(mi["moveInDate"]["Time"], '%Y-%m-%dT%H:%M:%SZ')
        moveIns["moveInDate"] = datetime_object
        moveIns["community"] = mi["name"]
        moveIns["bedrooms"] = mi["bedrooms"]["Float64"]
        moveIns["bathrooms"] = mi["bathrooms"]["Float64"]
        moveInList.append(moveIns)

    for lm in data4:
        leadMoveIns = {}
        datetime_moveIn= datetime.strptime(lm["moveInDate"]["Time"], '%Y-%m-%dT%H:%M:%SZ')
        if(len(lm["emailDateReceived"]["Time"])<=20):
            datetime_email = datetime.strptime(lm["emailDateReceived"]["Time"], '%Y-%m-%dT%H:%M:%SZ')
        else:
            datetime_email = datetime.strptime(lm["emailDateReceived"]["Time"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if(len(lm["phoneDateReceived"]["Time"])<=20):
            datetime_phone = datetime.strptime(lm["phoneDateReceived"]["Time"], '%Y-%m-%dT%H:%M:%SZ')
        else:
            datetime_phone = datetime.strptime(lm["phoneDateReceived"]["Time"], '%Y-%m-%dT%H:%M:%S.%fZ')
        leadMoveIns["moveInDate"] = datetime_moveIn
        leadMoveIns["emailDateReceived"] = datetime_email
        leadMoveIns["phoneDateReceived"] = datetime_phone
        leadMoveIns["community"] = lm["community"]
        leadMoveIns["bedrooms"] = lm["bedrooms"]["Float64"]
        leadMoveIns["bathrooms"] = lm["bathrooms"]["Float64"]
        leadMoveInList.append(leadMoveIns)

        datetime dt
        

    def defPricingGroup(community, bedrooms):
        if(community == "Emberwood Apartments" and bedrooms == 1):
            return "EBW1"
        elif(community == "Emberwood Apartments" and bedrooms == 2):
            return "EBW2"
        elif(community == "Emberwood Apartments" and bedrooms == 3):
            return "EBW3"
        elif(community == "Mill Pond II & III Apartments" and bedrooms == 2):
            return "MP2"
        elif(community == "Mill Pond II & III Apartments" and bedrooms == 3):
            return "MP3"
        elif(community == "Mill Pond Forest Apartments"):
            return "MPF"
        elif(community == "Gateway Green Townhomes"):
            return "GGT"
        elif(community == "Cedarwood Apartments" or community == "Greystone Apartments" or 
               community == "Pineridge Apartments" or "community" == "Birchview Apartments" or 
               community == "Maple Court Apartments"):
            return "CLASSIC"
        elif(mi["community"] == "256 Duplex" or mi["community"] == "243 House" or 
               mi["community"] == "555 House" or mi["community"] == "489 House" or 
               mi["community"] == "607 House"):
            return "HOUSE"

    counter1 = defaultdict(list)
    counter2 = defaultdict(list)

    counter1 = dict.fromkeys(['EBW1', 'EBW2', 'EBW3', 'MP2', 'MP3', 'MPF', 'HOUSE', 'GGT', 'CLASSIC', 'TOTAL'])
    for key in counter1:
        counter1[key] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    counter2 = dict.fromkeys(['EBW1', 'EBW2', 'EBW3', 'MP2', 'MP3', 'MPF', 'HOUSE', 'GGT', 'CLASSIC', 'TOTAL'])
    for key in counter2:
        counter2[key] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for mi in moveInList:
        if(present - timedelta(days=3*365) <= mi["moveInDate"] <= present):
            counter1["TOTAL"][mi["moveInDate"].month-1] = counter1["TOTAL"][mi["moveInDate"].month-1] + 1
            counter2["TOTAL"][mi["moveInDate"].day-1] = counter2["TOTAL"][mi["moveInDate"].day-1] + 1
            if(defPricingGroup(mi["community"], mi["bedrooms"]) == "EBW1"):
                counter1["EBW1"][mi["moveInDate"].month-1] = counter1["EBW1"][mi["moveInDate"].month-1] + 1
                counter2["EBW1"][mi["moveInDate"].day-1] = counter2["EBW1"][mi["moveInDate"].day-1] + 1
            elif(defPricingGroup(mi["community"], mi["bedrooms"]) == "EBW2"):
                counter1["EBW2"][mi["moveInDate"].month-1] = counter1["EBW2"][mi["moveInDate"].month-1] + 1
                counter2["EBW2"][mi["moveInDate"].day-1] = counter2["EBW2"][mi["moveInDate"].day-1] + 1
            elif(defPricingGroup(mi["community"], mi["bedrooms"]) == "EBW3"):
                counter1["EBW3"][mi["moveInDate"].month-1] = counter1["EBW3"][mi["moveInDate"].month-1] + 1
                counter2["EBW3"][mi["moveInDate"].day-1] = counter2["EBW3"][mi["moveInDate"].day-1] + 1
            elif(defPricingGroup(mi["community"], mi["bedrooms"]) == "MP2"):
                counter1["MP2"][mi["moveInDate"].month-1] = counter1["MP2"][mi["moveInDate"].month-1] + 1
                counter2["MP2"][mi["moveInDate"].day-1] = counter2["MP2"][mi["moveInDate"].day-1] + 1
            elif(defPricingGroup(mi["community"], mi["bedrooms"]) == "MP3"):
                counter1["MP3"][mi["moveInDate"].month-1] = counter1["MP3"][mi["moveInDate"].month-1] + 1
                counter2["MP3"][mi["moveInDate"].day-1] = counter2["MP3"][mi["moveInDate"].day-1] + 1
            elif(defPricingGroup(mi["community"], mi["bedrooms"]) == "MPF"):
                counter1["MPF"][mi["moveInDate"].month-1] = counter1["MPF"][mi["moveInDate"].month-1] + 1
                counter2["MPF"][mi["moveInDate"].day-1] = counter2["MPF"][mi["moveInDate"].day-1] + 1
            elif(defPricingGroup(mi["community"], mi["bedrooms"]) == "GGT"):
                counter1["GGT"][mi["moveInDate"].month-1] = counter1["GGT"][mi["moveInDate"].month-1] + 1
                counter2["GGT"][mi["moveInDate"].day-1] = counter2["GGT"][mi["moveInDate"].day-1] + 1
            elif(defPricingGroup(mi["community"], mi["bedrooms"]) == "CLASSIC"):
                counter1["CLASSIC"][mi["moveInDate"].month-1] = counter1["CLASSIC"][mi["moveInDate"].month-1] + 1
                counter2["CLASSIC"][mi["moveInDate"].day-1] = counter2["CLASSIC"][mi["moveInDate"].day-1] + 1
            elif(defPricingGroup(mi["community"], mi["bedrooms"]) == "HOUSE"):
                counter1["HOUSE"][mi["moveInDate"].month-1] = counter1["HOUSE"][mi["moveInDate"].month-1] + 1
                counter2["HOUSE"][mi["moveInDate"].day-1] = counter2["HOUSE"][mi["moveInDate"].day-1] + 1

    
    df = pd.DataFrame.from_dict(counter1)
    #html = '<h3> {df} </h3>'
    #return html.format(df=os.getenv("df", df.to_html()))#, hostname=socket.gethostname())
    width = 0.5
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    fig, ax = plt.subplots()
    plt.bar(months, counter1["TOTAL"], width, color='g')
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    buffer = b''.join(buf)
    b2 = base64.b64encode(buffer)
    fig2=b2.decode('utf-8')
    #df=os.getenv("df", df.to_html())
    return render_template("pydoc.html", data = df, fig = fig2)
    #return render_template("pydoc.html", fig = fig2)



@app.route('/images/<counter1>')
def images(counter1):
    return render_template("pydoc.html", counter1 = counter1)

    
@app.route("/fig/<counter1>")
def fig(counter1):
#    fig, ax = plt.subplots()
    #///fig = plt.figure()
    width = 0.5
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    fig = plt.bar(months, counter1["TOTAL"], width, color='g')
    img = StringIO()
    plt.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')

    #///html = '<h3> {df} </h3>' + '<img src=\'data:image/png;base64,{}\'>'.format(encoded) 
    # ''
    #"<img src='my_plot.png'>"

    #return render_template("images.html", title=cropzonekey)
    
#    plt.bar(months, counter1["TOTAL"], width, color='g')
#    fig.savefig('my_plot.png')
#    plt.show()

    #html = "<img src="{{ url_for('fig', counter1 = counter1)}}" alt="Image Placeholder" height="100">"
    
    #///tmpfile = BytesIO()
    #///fig.savefig(tmpfile, format='png')
    #///encoded = base64.b64encode(tmpfile.getvalue())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

