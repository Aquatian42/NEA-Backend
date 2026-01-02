import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import datetime

def get_past_data(latitude, longitude):
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)


    url = "https://archive-api.open-meteo.com/v1/archive"

    #compute date now and date 10 years ago
    date_now = str(datetime.datetime.now())[:10]
    date_ten_ya = date_now[:2] + str(int(date_now[2:4]) - 10) + date_now[4:]

    #parameters to give to open-meteo to get required 10 years of hourly temperature data
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date_ten_ya,
        "end_date": date_now,
        "hourly": "temperature_2m",
    }

    #fetch data
    responses = openmeteo.weather_api(url, params=params)
    
    #format data into a list from weird openmeteo format :(
    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_dataframe = pd.DataFrame(data = hourly_data)

    return list(hourly_dataframe["temperature_2m"])