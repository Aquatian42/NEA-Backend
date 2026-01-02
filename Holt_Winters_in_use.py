from utils import *

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
        self.data_to_forecast = self.past_data[:self.forecast_length]
        self.smooth_past_data()

def forecast_from_data(past_data):
    model = Holt_winters(past_data)
    model.do_smoothing()
    return model.forecast_data
