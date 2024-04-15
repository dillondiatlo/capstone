import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import datetime
import pickle
import requests, json
import random

#-------SETTINGS------#
#[theme]
primaryColor="#755104"
backgroundColor="#f7b731"
secondaryBackgroundColor="#0f0a00"
textColor="#fefaf3"

#Opening borough lists of taxi zones
with open('./Boroughs_List.pkl', 'rb') as f:
    Bronx, Manhattan, Brooklyn, Queens, Staten_Island = pickle.load(f)

#Opening model
with open ('./final_model.pkl', 'rb') as a:
    model = pickle.load(a)

#Displaying headerimage
st.image('fareforcaster.png')



#-------TITLES------#
#Page Title & Subtitle
st.title(":oncoming_taxi: :rainbow[Welcome to Fare Forecaster!] :oncoming_taxi:") 
st.subheader("""Make your selections on the left and we'll do the rest""")



#-------SIDEBAR------#
#Sidebar Title & Subtitle
st.sidebar.header(""":moneybag: Optimize your income :moneybag:""")

#________Borough------#
st.sidebar.subheader("""Select your borough below""")
borough_pick = st.sidebar.selectbox("Borough", ("Select Borough", "Manhattan", "Queens", "Brooklyn", "Bronx", "Staten Island"))

#________Congestion Surcharge------#
#Question
st.sidebar.subheader(""":rainbow[Is it rush hour?]""")

rush_hour = st.sidebar.radio('',["Yes", "No"],
    captions = ["When is it not?", "Surprisingly no."],
    index=None,
    )

if rush_hour == "Yes":
    surcharge = 2.75
elif rush_hour == "No":
    surcharge = 0



#________Precipitation------#
#Question
st.sidebar.subheader(""":rainbow[What's the weather like?]""")
weath = st.sidebar.radio('',["All clear :partly_sunny:", "It's raining :rain_cloud:", "Snow (of course) :snowflake:",
                              "Rainy ***and*** snowy :rain_cloud: :snowflake:", "Freezing rain :rain_cloud: :cold_face:", 
                              "Rain, snow, AND Ice? :rain_cloud: :snowflake: :ice_cube:!", ":rainbow[That's hail] :ice_cube: :eyes:"],
    captions = ["Heck yeah", "When is it not?", "Stay warm!", "Gross.", "At least we're in a car", "Drive careful!", "Oy vei!" ],
    index=None,
    )

if weath == "All clear :partly_sunny:":
    weath = 0
elif weath == "It's raining :rain_cloud:":
    weath = 1
elif weath == "Snow (of course) :snowflake:":
    weath = 2
elif weath == "Rainy ***and*** snowy :rain_cloud: :snowflake:":
    weath = 3
elif weath == "Freezing rain :rain_cloud: :cold_face:":
    weath = 4
elif weath == "Rain, snow, AND Ice? :rain_cloud: :snowflake: :ice_cube:!":
    weath = 5
elif weath == ":rainbow[That's hail] :ice_cube: :eyes:":
    weath = 6


# Get the current time
now = datetime.datetime.now()

# Get the current hour
h = now.hour
m = now.minute


# ------ Getting Weather API for Temp ------ #

# base URL
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
# City Name CITY = "Hyderabad"
CITY = "New York City"
# API key
API_KEY = st.secrets["api_key"]
# upadting the URL
URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
# HTTP request
response = requests.get(URL)

# checking the status code of the request
if response.status_code == 200:
  
   # getting data in the json format
   data = response.json()
   
   # getting the main dict block
   main = data['main']
   # getting temperature
   temperature = round((main['temp'] - 273.15) * 9/5 + 32, 2)
   # weather report

st.sidebar.write(f"Temperature: {temperature}")

# ------ Getting Day of the Week ------ #

#Creating today variable
today = datetime.date.today()

# Getting day of week
day_of_week = today.weekday()

# Converting to string
day_of_week_name = datetime.date.today().strftime("%A")

#Getting month
month = today.month

#Getting day of the month
day_of_month = today.day

# ------ Getting Ideal Trip Length ------ #
miles = random.randint(5, 10)
duration = random.randint(15, 25)







def answer(borough_pick):
    preds = []
    hoods = [Bronx, Manhattan, Brooklyn, Queens, Staten_Island]
    if borough_pick != "Select Borough" and rush_hour != None and weath != None:
        selected_borough = globals()[borough_pick.replace(" ", "_")]
        for zone in selected_borough:
            data = {
                "trip_miles": miles,
                "congestion_surcharge": surcharge,
                "temp": temperature,
                "preciptype": weath,
                "zone": zone,
                "trip_duration": duration,
                "month": month,
                "day_of_month": day_of_month,
                "borough_name": borough_pick,
                "day_of_week": day_of_week_name,
                "hour": datetime.datetime.now().hour,
                "minute":m  
            }
            df = pd.DataFrame(data, index=[0])
            y = model.predict(df)
            preds.append((zone, y))
        max_pred = max(preds, key=lambda x: x[1])
        return max_pred

result = answer(borough_pick)
if result:
    rounded = np.round(result[1], 2)
    rounded = ''.join(map(str, rounded))
    st.subheader("""Result:""")
    st.title(f"Head to {result[0]} and you'll make about ${rounded} per trip right now.")