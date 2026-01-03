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
temperatures = temperatures[0:]



class Holt_winters:
    def __init__(self, past_data=list, forecast_length=168, season_length=24):
        self.past_data = past_data
        self.forecast_length = forecast_length
        self.season_length = season_length
        
        self.smoothed_data = []
        self.seasonal_components = []
        self.forecast_data = []

    def do_smoothing(self):
        #must be between 0 and 1 for all
             
        best_mse = float('inf')
        best_params = {}
        
        datalist = chunks_of_list(self.past_data,50,1680)

        # test out combinations of coefficients 

        y = 0
        x = 0.5
        z = 0.1
        while y < 1:
            y += 0.1
            self.beta = z
            self.alpha,self.beta,self.gamma = x,y,z
            mserrors = []
            for data in datalist:
                self.data_to_forecast = data[:-self.forecast_length]
                self.correct_data = data[-self.forecast_length:]
                # reset for each set of parameters
                self.smoothed_data = []
                self.forecast_data = []

                self.smooth_past_data()
                current_mse = mse(self.forecast_data,self.correct_data)
                mserrors.append(current_mse)

            avg_mserror = mean(mserrors)
            current_mse = avg_mserror
            if current_mse < best_mse:

                best_mse = current_mse
                best_params = {'alpha': x, 'beta': y, 'gamma': z}
        
        print(f"Best mse: {best_mse}")
        print(f"Best Parameters: {best_params}")
        # Rerun with best parameters for plotting
        if best_params:
            self.alpha = best_params['alpha']
            self.beta = best_params['beta']
            self.gamma = best_params['gamma']
            self.data_to_forecast = self.past_data[:]
            self.smoothed_data = []
            self.forecast_data = []
            self.smooth_past_data()
    
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
        self.initialise_components()

        previous_level = self.initial_level
        previous_trend = self.initial_slope
        
        # not all seasonals need to be stored - just the seasonal length worth
        current_seasonal_components = self.initial_seasonalcomponents.copy()
        
        # smoothing  
        for t in range(len(self.data_to_forecast)):
            seasonal_index = t % self.season_length
            previous_seasonal_component = current_seasonal_components[seasonal_index]

            self.smoothed_data.append(previous_level + previous_trend + previous_seasonal_component)

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
            forecast_value = previous_level + (k * previous_trend) + seasonal_component
            self.forecast_data.append(forecast_value)
thetime = time.time()

temperatures = temperatures[67579:300245]
print(f"Original data points: {len(temperatures)}")
Test = Holt_winters(temperatures[:-336], 336, 24)
Test.do_smoothing()
print(f"Smoothed data points: {len(Test.smoothed_data)}")
print(time.time()-thetime)

plt.figure(figsize=(14, 7))
plt.plot(temperatures, label='Original Data', color='blue')

# Create a correct x-axis for the forecast to plot it after the smoothed data
forecast_index = range(len(Test.smoothed_data), len(Test.smoothed_data) + len(Test.forecast_data))
plt.plot(forecast_index, Test.forecast_data, label='Forecast Data', color='red', linestyle='--')

plt.plot(Test.smoothed_data, label='Smoothed Data (Fit)', color='orange')
plt.title('Holt-Winters Smoothing + Forecasting')
plt.xlabel('Time Steps')
plt.ylabel('Temperature')
plt.legend()
plt.grid(True)
plt.show()
