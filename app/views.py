from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
import re
import sqlite3
from nsepy import get_history
import matplotlib.pyplot as plt
from mplfinance import candlestick_ohlc
import time
from datetime import date
import datetime
import pandas as pd
import numpy as np
import requests
import numpy as np
import pandas as pd
import bokeh
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.embed import components
bv = bokeh.__version__
from math import pi
from bokeh.models import HoverTool, ColumnDataSource, Label
from . import arima as arima


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            stockname=request.POST['stockname']
            startdate=request.POST['startdate']
            enddate=request.POST['enddate']
            print(stockname)
            print(startdate)
            print(enddate)
            s=startdate.split("-")
            e=enddate.split("-")
            print(s[0])
            print(s[1])
            print(s[2])
            
            df = get_history(symbol=stockname,start=date(int(s[0]),int(s[1]),int(s[2])),end=date(int(e[0]),int(e[1]),int(e[2])))
            filename=stockname+".csv"
            df.to_csv(filename)
            df.dropna(inplace = True)
            
            plot_array = np.zeros([len(df), 5])
            plot_array[:, 0] = np.arange(plot_array.shape[0])
            
            print("dataset")
            print(df)
            print(df.iloc[:, 0:5])
            df = pd.read_csv(filename) 
            print(df.head())
            df=df.drop(['Symbol','Series','Prev Close','Last','VWAP','Volume','Turnover','Trades','Deliverable Volume','%Deliverble'], axis=1)
            df.Date = pd.to_datetime(df.Date)
            print('DF CLOSE')
            print(df.Close)
            print(df.Date)
            inc = df.Close > df.Open
            dec = df.Open > df.Close
            w = 12*60*60*1000 # half day in ms
            
            p = figure(plot_width=900, plot_height=500, title=stockname+"Chart", x_axis_type="datetime",x_axis_label="Days",y_axis_label="Stock Status")
            #pylint: disable-msg=too-many-arguments
            p.line(df.Date, df.Close, line_width=2, line_color="#FB8072",legend='Price')#pylint: disable=R0913
            p.xaxis.major_label_orientation = pi/4
            #pylint: disable-msg=too-many-arguments
            p.grid.grid_line_alpha=0.3
            p.segment(df.Date, df.High, df.Date, df.Low, color="black")#pylint: disable=R0913
            p.vbar(df.Date[inc], w, df.Open[inc], df.Close[inc], fill_color="green", line_color="black")#pylint: disable=R0913
            p.vbar(df.Date[dec], w, df.Open[dec], df.Close[dec], fill_color="red", line_color="black")#pylint: disable=R0913

            script, div = components(p)
            forecast=arima.process(filename)
            dates=forecast.index
            l=[]
            for i in forecast:
                l.append(i)
            frcst_lst=[]
            for i in range(len(dates)):
                dt_fr=str(dates[i])[:10]+'    :    '+str(l[i])[:6]
                frcst_lst.append(dt_fr)
            return render(request,'graph.html',{'bv':bv,'script':script,'div':div,'frcst_lst':frcst_lst})
        return render(request,'stock.html')
    else:
        return redirect('/login')

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.error(request,'INVALID CREDENTIALS,Please try again.')
            return redirect('/login')
    return render(request,'login.html')

def signup(request):
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        username=request.POST['username']
        email=request.POST['email']
        password1=request.POST['password1']
        password2=request.POST['password2']
        if password1!=password2:
            messages.info(request,'PASSWORDS DID NOT MATCH')
            return render(request,'signup.html')
        elif User.objects.filter(username=username).exists():
            messages.info(request,'oops!!USERNAME TAKEN')
            return redirect('/signup')
        elif User.objects.filter(email=email).exists():
            messages.info(request,'oops!!Email ALREADY IN USE')
            return redirect('/signup')
        else:
            user=User.objects.create_user(username=username,password=password1,email=email,first_name=fname,last_name=lname)
            user.save()
            messages.info(request,'USER CREATED')
            return redirect('/login')
    return render(request,'signup.html')

def logout(request):
    auth.logout(request)
    return redirect('/')