import matplotlib.pyplot as plt
from utils import *
import csv

# temperatures = [13.9,13.7,13.8,13.6,13.9,14.1,13.8,14.5,15.8,17.1,18.3,19,19.1,19,18.8,18.2,17.7,18.6,18.3,17.2,16.3,16,15.3,14.9,14.1,13.3,12.7,12.4,12.2,11.9,12,12.8,13.9,15.4,16.7,17.7,18,17.5,17.6,17.7,17.5,16.9,17.1,16.6,16,15.6,15.4,15.4,15.3,15.5,15.6,15.4,14.9,14.5,14.3,14.3,14.9,16.7,18.8,19.8,20.5,20.4,18.9,16.8,17.2,18.2,17.9,17.1,16.3,15.9,15.4,14.9,14.4,14,13.6,13.1,12.6,12.2,12.2,12.9,13.4,14,14.1,14.5,15.1,14.6,14.9,15.5,15.7,15.9,15.6,14.5,13.9,13.6,13.2,12.7,11.9,11.4,11.1,11.1,11,11,10.9,11.6,13,14.8,16.1,17,18,19,19.1,19.4,19.5,19.1,19,18.3,17.5,17.4,16.6,15.9,15.4,14.9,14.7,13.9,14,13.9,13.4,13.5,14.4,15.6,17.3,18.8,20.6,21.4,21.9,22.2,22.1,21.6,20.7,19.3,18.2,17.4,16.6,16,16,15.8,15.5,15.3,15,14.9,14.9,15.5,16.8,18.6,19.8,20.8,21.2,21.2,22.4,22.9,23,23,22.2,20.7,19.2,18.4,17.8,16.9,15.2,14.6,13.8,13.4,13.6,13.5,12.7,12.9,13.9,15,16,16.8,18,18.7,19.6,19.4,19.5,15.3,16.3,15.6,15.3,14.4,13.5,12.9,12.6,12.3,11.9,11.7,11.2,10.8,10.3,11.1,12.4,14.5,16.1,17.1,18.6,19.2,20,20.4,20.2,19.5,18.5,17.7,16.8,16.2,15.5,15,14.8,14.4,14.1,13.6,13.4,13.2,13,13,13.9,14.6,15.4,16,17.5,18.8,17.8,16.7,16.6,16.5,16,15.2,15.5,15.1,14.2,13.5,13,12.7,12.4,11.9,11.4,11.1,11.4,12,13.2,14.4,15.5,15.9,15.3,14.4,15.9,15.5,15.7,15.1,14,13.3,12.9,12.3,12.2,11.9,11.4,11,10.7,10.6,10.6,10.3,10.3,10.7,11.9,13.4,14.5,15.7,16.8,17.2,17.2,17.6,15.7,16,15.4,14.7,13.7,13.1,12.5,11.8,11.8,11.7,11.7,11.4,11.3,11.4,11.5,11.7,12.6,13.9,14.7,15.4,16.2,15.2,16.3,15.5,15.3,15.7,15.1,14,13.2,12.6,12.1,11.6,11,10.3,9.9,9.6,9.4,9.1,8.9,9.4,10.5,12,13.1,13.8,14.2,13.8,14.3,13.4,13,13.1,13.3,14.3,15.5,16.5,15.9,15.5]
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
temperatures = temperatures[:]

class Holt_winters:
    def __init__(self, past_data=list, forecast_length=168, season_length=24):
        self.past_data = past_data
        self.forecast_length = forecast_length
        self.season_length = season_length
        
        self.smoothed_data = []
        self.seasonal_components = []
        self.forecast_data = []
    
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
            seasonal_index = t % self.season_length
            previous_seasonal_component = current_seasonal_components[seasonal_index]

            ##### NOT USING TREND!!!!!!!
            self.smoothed_data.append(previous_level + previous_trend * 0 + previous_seasonal_component)

            y = self.data_to_forecast[t]
            
            level = self.alpha * (y - previous_seasonal_component) + (1 - self.alpha) * (previous_level + previous_trend)
            
            trend = self.beta * (level - previous_level) + (1 - self.beta) * previous_trend
            
            current_seasonal_components[seasonal_index] = self.gamma * (y - level) + (1 - self.gamma) * previous_seasonal_component
            
            previous_level = level
            previous_trend = trend

        # forecast loop 
        for i in range(self.forecast_length):
            # k is the number of steps ahead to forecast
            k = i + 1
            # Get the appropriate seasonal component from the last full cycle
            seasonal_index = (len(self.data_to_forecast) + i) % self.season_length
            seasonal_component = current_seasonal_components[seasonal_index]

            # Forecast using the last level and trend from the historical data
            forecast_value = previous_level + (k * previous_trend * 0) + seasonal_component
            self.forecast_data.append(forecast_value)

    def do_smoothing(self):
        #must be between 0 and 1 for all
        self.alpha = 0.2
        self.beta = 0.05
        self.gamma = 0.5
        self.data_to_forecast = self.past_data[:-self.forecast_length]
        self.smooth_past_data()

print(f"Original data points: {len(temperatures)}")
Test = Holt_winters(temperatures, 120, 24)
Test.do_smoothing()
print(f"Smoothed data points: {len(Test.smoothed_data)}")


plt.figure(figsize=(14, 7))
plt.plot(temperatures, label='Original Data', color='blue')

forecast_index = range(len(Test.smoothed_data), len(Test.smoothed_data) + len(Test.forecast_data))
plt.plot(forecast_index, Test.forecast_data, label='Forecast Data', color='red', linestyle='--')

plt.plot(Test.smoothed_data, label='Smoothed Data (Fit)', color='orange')
plt.title('Holt-Winters Smoothing + Forecasting')
plt.xlabel('Time Steps')
plt.ylabel('Temperature')
plt.legend()
plt.grid(True)
plt.show()
