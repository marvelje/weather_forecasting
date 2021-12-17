# NYC Weather Forecasting Analysis

## Summary

This analysis compares 12 day weather forecasts to actual weather events for NYC. The data can be used for numerous weather related analyses, including "how different is the forecasted high / low temp different from the actual temp" and "when the forecast calls for a 20% chance of rain, does it actual end up raining 20% of the time"?

The data is scraped daily from three different websites (details below), with updates regularly pushed to this Github.

## Data

The data is scraped from 3 different websites using Beautiful Soup, and exported daily as an updated CSV file. The forecast and actual weather data is from the Central Park weather station in NYC. Data sources below:
* weather.com: 12-day forecast information for NYC, including high / low temp, wind speed / direction, and precipitation probability
* timeanddate.com: previous day actual high / low temp
* weather.gov (NOAA): previous day precipitation totals

Data is scraped daily (minus a few days in November) and appended to the existing dataframe, then saved as a CSV file. Current coverage starts from 9/18/2021

## Analyses

While I hope to add to this continuously, a couple analyses that I've already run include:

### Actual vs. Forecast Temperature

The below shows the difference between the forecast temp and actual temp, split by number of days out. The day before, the high temp is generally very accurate, within 2 degrees on average. However, the high temp miss shows greater variability and becomes significantly less reliable the further out you are. On the other hand, the low temp has a greater miss on average the day before, but shows much less variability.

![image](https://user-images.githubusercontent.com/81099027/146255963-450c450f-68ca-4d1c-956b-3cbd976bb9c2.png)

### Precipitation Probability

When the forecast calls for a 20% or less chance of rain, I often assume this means that it won't rain at all. In theory, it should rain about 20% of the time! From the below, you can see that on the day before, when calling for 0-20% chance of rain, the forecasters get it roughly correct, as it usually ends up raining about 20% of the time. However, this accuracy quickly drops off. While this starts to suffer from small sample size issues, when the forecast is 4+ days out and callinging for 0-20% chance of rain, it actually ends up raining more than half the time! This just goes to show how difficult it is to forecast out more than a few days, particularly for precipitation.

![image](https://user-images.githubusercontent.com/81099027/146256532-be34f990-1e1f-486d-a7b8-e9585eb683a3.png)
