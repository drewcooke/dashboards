#!/usr/bin/env python

numMax = 10
dest = "/var/www/html/pages/index.html"

import time, datetime, sys, os
os.environ[ 'MPLCONFIGDIR' ] = '/tmp/'
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
pd.options.display.max_colwidth = 200

st_day = datetime.datetime.today().weekday()
st_time = datetime.datetime.now().time()

f = open("/home/ec2-user/flip/hour_start.txt", "r")
hour_start = int(f.readlines()[0])
f.close()

f = open("/home/ec2-user/flip/hour_end.txt", "r")
hour_end = int(f.readlines()[0])
f.close()

f = open("/home/ec2-user/flip/hour_diff.txt", "r")
hour_diff = int(f.readlines()[0])
f.close()

if hour_start == 0:
    sys.exit()

if (st_day > 4) | (st_time < datetime.time(hour_start,30)) | (st_time > datetime.time(hour_end,1)):
    sys.exit()

print("page start: ", datetime.datetime.now())

### STOCK POPULATION ###

os.chdir("/home/ec2-user/data")
x = pd.read_pickle('alertsValRats.pkl')
x = x[x['time']>=(time.time()-7*3600)]
xg = x.groupby('symbol')['time'].max().reset_index().sort_values('time',ascending=False)
xg['datetime'] = xg['time'].apply(lambda q: datetime.datetime.fromtimestamp(int(q)-3600*hour_diff).strftime('%Y-%m-%d %H:%M'))

st = pd.read_pickle('stats.pkl')
st = st[st.marketcap>0][['symbol']]

cp = pd.read_pickle('comps.pkl')
cp = cp.merge(st,on='symbol',how='inner')
cp = cp[['symbol','companyName','sector','industry']]
xg = xg.merge(cp,on='symbol',how='inner')

# Number of containers
if len(xg['symbol']) < numMax:
    numMax = len(xg['symbol'])

xg = xg.head(numMax)
#print(xg.head())

### CHART BUILD ###

from funct import graphNumDaysWithToday
for index, row in xg.iterrows():
    loc = '/var/www/html/pics/charts/'+row['symbol']+'-65days.png'
    graphNumDaysWithToday(row['symbol'],loc,65)

from funct import intraDay
for index, row in xg.iterrows():
    intraDay(row['symbol'],hour_diff)

###  CHECK NEWS ###
from funct import getNews
for index, row in xg.iterrows():
    getNews(row['symbol'],5)

### HTML BUILD ###

# HTML HEADER
f = open("/home/ec2-user/snip/htmlHeader.txt", "r")
html = f.read()
f.close()

html = html+"<body><table>"
for index, row in xg.iterrows():
    sym = row['symbol']
    firstAlert = row['datetime']
    info = row['companyName']+' - '+row['sector']+' - '+row['industry']
    html = html+"<div><tr><td><tr><h2>"+sym+" - "+firstAlert+" - "+info+"</h2></tr><tr>"
    html = html+"<embed src='../pics/charts/"+sym+"-65days.png' />"
    html = html+"<embed src='../pics/charts/"+sym+"-intraday.png' />"
    html = html+"</tr><tr><embed src='../news/"+sym+".html' />"
    html = html+"</tr></td></tr></div>"

html = html+"</table></body>"
#print(html)

# HTML WRITE
f = open(dest, "w")
f.write(html)
f.close()


print("page end:   ", datetime.datetime.now())
