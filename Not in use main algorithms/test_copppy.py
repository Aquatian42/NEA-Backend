import time
import matplotlib.pyplot as plt
from utils import *
import csv

csvFile = csv.reader(open(r"C:\Users\tomto\Data\School\Computer-Science\NEA\1975\Bleneau_Festiniogg.csv", mode="r"))
csvList = []

for line in csvFile:
    csvList.append(line)
csvList = csvList[4:]


dates,temperatures,humidity,dew_points,apparent_temperatures,rainfall,snowfall,sea_level_pressure,wind_speed_10m,wind_speed_100m,wind_direction_10m,wind_direction_100m,wind_gusts_10m,cloud_cover,pressure = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
for line in csvList:
    dates.append(int(line[0][0:4]+line[0][5:7]+line[0][8:10]+line[0][11:13]))
    temperatures.append(float(line[1]))
    humidity.append(float(line[2]))
    dew_points.append(float(line[3]))
    apparent_temperatures.append(float(line[4]))
    rainfall.append(float(line[5]))
    sea_level_pressure.append(float(line[6]))
    wind_speed_10m.append(float(line[7]))
    wind_speed_100m.append(float(line[8]))
    wind_direction_10m.append(float(line[9]))
    wind_direction_100m.append(float(line[10]))
    wind_gusts_10m.append(float(line[11]))
    cloud_cover.append(float(line[12]))
    pressure.append(float(line[13]))
temperatures = temperatures[24*10*365:24*25*365+100]


class Holt_winters:
    def __init__(self, past_data=list, forecast_length=168, season_length=24):
        self.past_data = past_data
        self.forecast_length = forecast_length
        self.season_length = season_length
        
        self.smoothed_data = []
        self.seasonal_components = []
        self.forecast_data = []

        self.damping = 0.98
    
    def initialise_components(self):
        #https://robjhyndman.com/hyndsight/hw-initialization/
        initialisation_data = self.past_data[:self.season_length * 2] 

        #level is set to the average of the first season's levels
        initial_level = mean(initialisation_data[:self.season_length])

        #slope is set to be the average of the difference between levels for each time in the first two seasons
        slopeslist = []
        for i in range(self.season_length):
            slopeslist.append(initialisation_data[i+self.season_length] - initialisation_data[i])
        # The initial slope is the average change per time step
        initial_slope = mean(slopeslist) / self.season_length

        #seasonality needs to be defined for a season's worth of data - using additive not multiplicative
        initial_seasonalcomponents = []
        # Subtract the mean of the first season (initial_level) to get seasonal component
        for i in range(self.season_length):
            initial_seasonalcomponents.append(initialisation_data[i] - initial_level)

        self.initial_level = initial_level
        self.initial_slope = initial_slope
        self.initial_seasonalcomponents = initial_seasonalcomponents.copy()

    def smooth_past_data(self):
        self.initialise_components()

        previous_level = self.initial_level
        previous_trend = self.initial_slope
        
        # not all seasonals need to be stored - just the seasonal length worth
        current_seasonal_components = self.initial_seasonalcomponents.copy()
        
        # smoothing  
        for t in range(len(self.data_to_forecast)):
            y = self.data_to_forecast[t]
            seasonal_index = t % self.season_length
            previous_seasonal_component = current_seasonal_components[seasonal_index]
            
            level = self.alpha * (y - previous_seasonal_component) + (1 - self.alpha) * (previous_level + previous_trend)
            
            trend = self.beta * (level - previous_level) + (1 - self.beta) * previous_trend
            
            current_seasonal_components[seasonal_index] = self.gamma * (y - level) + (1 - self.gamma) * previous_seasonal_component
            
            self.smoothed_data.append(previous_level + previous_trend + previous_seasonal_component)
            
            previous_level = level
            previous_trend = trend



        last_point = self.smoothed_data[-1] 
        seasonal_index = (len(self.data_to_forecast)) % self.season_length 
        seasonal_component = current_seasonal_components[seasonal_index]
        # Forecast using the last level and trend from the historical data
        forecast_value = previous_level + (previous_trend) + seasonal_component
        shift = last_point - forecast_value
        # print(last_point,forecast_value,shift)

        # forecast loop 
        for i in range(self.forecast_length):
            # Get the appropriate seasonal component from the last full cycle 
            seasonal_index = (len(self.data_to_forecast) + i) % self.season_length 
            seasonal_component = current_seasonal_components[seasonal_index]

            # Forecast using the last level and trend from the historical data
            forecast_value = previous_level + (i * previous_trend) + seasonal_component + shift ## not sure why shift needed?
            self.forecast_data.append(forecast_value)

            #Damping
            previous_trend *= self.damping


    def do_smoothing(self):
        #must be between 0 and 1 for all
        self.alpha = 0.2
        self.beta = 0.05
        self.gamma = 0.5
        self.data_to_forecast = self.past_data[:]
        self.smooth_past_data()



thetime = time.time()
print(f"Original data points: {len(temperatures)}")
Test = Holt_winters(temperatures[:-336], 240)
Test.do_smoothing()
print(f"Smoothed data points: {len(Test.smoothed_data)}")
print(time.time()-thetime)
print(Test.forecast_data[:10])
print(Test.smoothed_data[-10:])
temperatures = temperatures[(len(temperatures)%24):]
plt.figure(figsize=(14, 7))
plt.plot(temperatures, label='Original Data', color='blue')

# Create a correct x-axis for the forecast to plot it after the smoothed data
forecast_index = range(len(Test.smoothed_data), len(Test.smoothed_data) + len(Test.forecast_data))
plt.plot(forecast_index, Test.forecast_data, label='Forecast Data', color='red', linestyle='--')

plt.plot(Test.smoothed_data, label='Smoothed Data (Fit)', color='orange')
plt.title('Seasonal Exponential Smoothing + Forecasting')
plt.xlabel('Time Steps')
plt.ylabel('Temperature')
plt.legend()
plt.grid(True)
plt.show()