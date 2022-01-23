#!/usr/bin/env python
# coding: utf-8

# # Weather Scraping
# 
# - This script scrapes weather data from three different sources
#     - weather.com for the 15 day NYC forecast (Central Park station)
#     - timeanddate.com for prior day high and low
#     - weather.gov for prior day rainfall

# In[1]:


from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import datetime as dt


# In[2]:


# Read in existing weather history
try:
    weather_hist = pd.read_csv('./Data/nyc_forecast.csv')
except FileNotFoundError:
    pass


# ## The Weather Channel 
# 
# Source for NYC 10 day forecast high & low temps, precipation probability, and wind direction / speed

# In[3]:


url = 'https://weather.com/weather/tenday/l/New+York+City+NY?canonicalCityId=a701ee19c4ab71bbbe2f6ba2fe8c250913883e5ae9b8eee8b54f8efbdb3eec03'

res = requests.get(url)

soup = BeautifulSoup(res.content)


# In[4]:


date_headers = soup.find_all('h2', class_='DetailsSummary--daypartName--2FBp2')


# In[5]:


# Pull in each of the dates in the forecast

dates = []

for date in date_headers:
    dates.append(date.text)
    
# Convert the numbers to actual dates

tomorrow = dt.date.today() + dt.timedelta(1)
dates = [tomorrow + dt.timedelta(days=i) for i in range(len(dates))]

# Create list of days
# In future, just extract from the datetime column. Having issues with this though.
days = []
months = []
years = []

for i, date in enumerate(dates):
    if (i + 1) == len(dates):
        continue
    else:
        days.append(date.day)
        months.append(date.month)
        years.append(date.year)


# In[6]:


# Pull in daily high temperatures and add to a high temp list

Htemps = soup.find_all(class_="DetailsSummary--highTempValue--3Oteu")

high_temps = []

for i,temp in enumerate(Htemps):
    if i == 0:
        continue
    else:
        high_temps.append(temp.text)


# In[7]:


# Pull in low temperatures and add to a low temp list

Ltemps = soup.find_all(class_="DetailsSummary--lowTempValue--3H-7I")

low_temps = []

for i, temp in enumerate(Ltemps):
    if i == 0:
        continue
    else:
        low_temps.append(temp.text)


# In[8]:


# Convert the temperatures to integers. This needs to be run early enough in the day that the page still has a high.

for i in range(min(len(low_temps), len(high_temps))):
    low_temps[i] = int(low_temps[i].strip('°'))
    high_temps[i] = int(high_temps[i].strip('°'))


# In[9]:


# Pull the precipitation probability

precip_headers = soup.find_all(class_='DetailsSummary--precip--1ecIJ')

precip_prob = []

for i,day in enumerate(precip_headers):
    if i ==0:
        continue
    else:
        precip_prob.append((day.find_all('span'))[0].text)
    
# Convert precip probability to a decimal

precip_prob = [float(x.strip('%')) / 100 for x in precip_prob]


# In[10]:


# Pull in wind stats

wind_stats = []

wind_scrape = soup.find_all(class_='Wind--windWrapper--3aqXJ undefined')

for i,day in enumerate(wind_scrape):
    if i == 0:
        continue
    else:
        wind_stats.append(day.text)


# In[11]:


# Create a dictionary with all the information

num_days = len(high_temps)

forecast_detail = {}
forecast_dict = {}

forecast_date = dt.date.today()

for i in range(num_days):
    forecast_detail[dates[i]] = {'high_temp': high_temps[i], 'low_temp': low_temps[i], 
                                 'precip_prob': precip_prob[i], 'wind_stats': wind_stats[i]}
    
forecast_dict[forecast_date] = forecast_detail


# In[12]:


# Transform dict into a dataframe

weather_df = pd.DataFrame.from_dict(forecast_dict[forecast_date]).T

weather_df['forecast_date'] = forecast_date

# Convert the forecast date column to a datetime object
weather_df['forecast_date'] = pd.to_datetime(weather_df['forecast_date'])

weather_df['date'] = weather_df.index

weather_df['day'] = days
weather_df['month'] = months
weather_df['year'] = years

weather_df.set_index('forecast_date', inplace=True)

weather_df.reset_index(inplace=True)


# ## Time and Date
# 
# Source for yesterday's actual high and low temperatures in NYC

# In[13]:


url2 = 'https://www.timeanddate.com/weather/usa/new-york/historic'

res2 = requests.get(url2)

soup2 = BeautifulSoup(res2.content)


# In[14]:


yest_summary = soup2.find(class_ = 'eight columns')

yest_summary_p = yest_summary.find_all('p')

yest_text = yest_summary_p[0].text

actual_max = int(yest_text.split(': ')[1][:2])
actual_min = int(yest_text.split(': ')[2][:2])


# ## Create empty columns for actual weather data

# In[15]:


# Create columns for actual high, low, and precipitation

weather_df['actual_high'] = np.nan
weather_df['actual_low'] = np.nan
weather_df['actual_precip'] = np.nan


# ## NOAA Weather.gov
# 
# Used to pull prior day rainfall

# In[16]:


url3 = 'https://w1.weather.gov/data/obhistory/KNYC.html'

res3 = requests.get(url3)

soup3 = BeautifulSoup(res3.content)


# In[17]:


# Pull all table tags then only pull the main table (index 3)

tables = soup3.find_all('table')

full_table = tables[3]

# Filter for only the subset of the table with actual data

table_subset = full_table.find_all('tr')[3:-3]


# In[18]:


# Loop through table and pull all data

rows = {}

for i in range(len(table_subset)):
    items_to_append = []
    
    table_row = table_subset[i].find_all('td')
    
    for item in table_row:
        items_to_append.append(item.text)
    
    rows[i] = items_to_append


# In[19]:


# Convert table to Data Frame and rename the columns

rain_history = pd.DataFrame.from_dict(rows).T

# Rename columns

old_cols = list(range(18))

columns = ['Date', 'Time_EDT', 'Wind_mph', 'Vis_mi', 'Weather', 'Sky_cond', 'Air_temp', 'Dewpoint', 'Max_6hr',
          'Min_6hr', 'Humidity', 'Wind_chill', 'Head_index', 'Pressure_inches', 'Pressure_mb',
          'precip_1hr', 'precip_3hr', 'precip_6hr']

cols_dict = dict(zip(old_cols, columns))

rain_history.rename(columns=cols_dict, inplace=True)


# In[20]:


# Convert 'date' column to int

rain_history['Date'] = rain_history['Date'].apply(lambda x: int(x))


# In[21]:


rain_history


# In[22]:


# Make sure precipitation columns are int as well

precip_cols = ['precip_1hr', 'precip_3hr', 'precip_6hr']

rain_history[precip_cols] = rain_history[precip_cols].replace('', np.nan)

rain_history[precip_cols] = rain_history[precip_cols].applymap(lambda x: float(x))


# ## Append to existing dataframe
# 
# Take new dataframe with current 10-day forecast and append to existing dataset

# In[23]:


# Append new data to existing file. If this is the first day running this script, set dataframe for
# export equal to new dataframe

try:
    weather_hist = weather_hist.append(weather_df, ignore_index=True)
except NameError:
    weather_hist = weather_df


# In[24]:


# Drop "Unnamed" column if it appears (should really figure out at some point how this sneaks in)

try:
    weather_hist.drop(columns=['Unnamed: 0'], inplace=True)
except KeyError:
    pass


# In[25]:


# One time conversion of the forecast date column to type datetime

# weather_hist['forecast_date'] = pd.to_datetime(weather_hist['forecast_date'])


# ## Merge in rainfall and actual temperature history

# In[26]:


pd.set_option('display.max_rows', None)


# In[27]:


# One time addition of month / year columns

# weather_hist['year'] = 2021
# weather_hist['month'] = 9
# weather_hist.loc[weather_hist['day'] <= 10, 'month'] = 10


# In[28]:


# Find location where of yesterday's date. Need to fix so it isn't just the day.

yest_date = forecast_date - dt.timedelta(1)

day_locs = weather_hist.index[(weather_hist['day'] == yest_date.day) & (weather_hist['month'] == yest_date.month)
                        & (weather_hist['year'] == yest_date.year)].tolist()

# i = np.where(weather_hist['day'] == yest_date.day)


# In[29]:


rain_day = rain_history.groupby('Date').precip_1hr.sum()


# In[30]:


try:
    weather_hist.iloc[day_locs,weather_hist.columns.get_loc('actual_precip')] = rain_day.iloc[rain_day.index.get_loc(yest_date.day)]
except IndexError:
    pass


# In[31]:


# Put actual min and max temps in where Date = yesterday

try:
    weather_hist.iloc[day_locs,weather_hist.columns.get_loc('actual_high')] = actual_max
    weather_hist.iloc[day_locs,weather_hist.columns.get_loc('actual_low')] = actual_min
except IndexError:
    pass


# In[32]:


# weather_hist


# ## Export to CSV

# In[33]:


weather_hist.to_csv('./Data/nyc_forecast.csv')


# ## Below here not in use
# 
# Haven't been able to successfully scrape follwing website
# - Old Farmer's Almanac (403 error)
# - Weather underground. Trouble pulling data because tags have extraneous labeling that I'm not familiar with

# ## Old Farmer's Almanac
# 
# Used to pull precipitation history. Received a 403 code in response.

# In[34]:


# url3 = 'https://www.almanac.com/weather/history/NY/New%20York'

# res3 = requests.get(url3)

# soup3 = BeautifulSoup(res3.content)


# ## Weather Underground
# 
# Precipitation history. Again, I'm having issues with this.

# In[35]:


# url3 = 'https://www.wunderground.com/history/daily/us/ny/new-york-city/yesterday'

# res3 = requests.get(url3)

# soup3 = BeautifulSoup(res3.content)


# In[36]:


# test = soup3.find_all('td')


# In[37]:


# table_bodies = soup3.find_all(class_ = 'ng-star-inserted')

