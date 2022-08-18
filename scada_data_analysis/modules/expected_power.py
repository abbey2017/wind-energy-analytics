"""
This module is used to estimate the expected power of a wind turbine generator.
"""
import sys
import numpy as np
import pandas as pd

from scipy.interpolate import interp1d

sys.path.append('')

from scada_data_analysis.utils.binning_function import binning_func
from scada_data_analysis.modules.power_curve_preprocessing import PowerCurveFiltering

class ExpectedPower:
    def __init__(self, turbine_label, windspeed_label, power_label, method=None, kind=None,
                 cut_in_speed=3, bin_interval=0.5, z_coeff=2, filter_cycle=5) -> None:
        """
        turbine_label:   Column name of unique turbine identifiers or turbine names
        windspeed_label: Column name of wind speed
        power_label:     Column name of active power
        method:          Specifies method for estimating expected power from processed training data.
                         The string has to be 'binning' or 'autoML'
        kind:            Only applies to the binning method and specifies the kind of interpolation
                         to apply on binned data points. Available methods are: 'linear', 'quadratic' and 'cubic'.
                         Quadratic and cubic methods use spline interpolation of second and third order respectively.
        cut_in_speed:    Cut in speed of turbine
        bin_interval:    Wind speed bin interval
        z_coeff:         Threshold of standard deviation used in filter 
                         within which operational data is considered normal
        filter_cycle:    Number of times to pass scada data through filter
        """
        
        self.turbine_label = turbine_label
        self.windspeed_label = windspeed_label
        self.power_label = power_label
        self.method = method
        self.kind = kind
        self.cut_in_speed = cut_in_speed
        self.bin_interval = bin_interval
        self.z_coeff = z_coeff
        self.filter_cycle = filter_cycle
        
    
    def fit(self, training_data):
        """
        Method to create models based on training data
        
        training_data:   Pandas dataframe of scada data for extracting
                         production benchmark (typical operating condition)
        """
        
        # initialize power curve processing class
        pc_filter = PowerCurveFiltering(self.turbine_label, self.windspeed_label, self.power_label,
                                        training_data, self.cut_in_speed, self.bin_interval, self.z_coeff, self.filter_cycle)

        # get data points during normal operating conditions (filtered data)
        self.normal_df, _ = pc_filter.process()
        
        # get unique turbine names in training data
        self.turbine_names = self.normal_df[self.turbine_label].unique()
        
        # instantiate a dictionary to store prediction functions and max power for each turbine
        self.pred_funcs_dict = dict()
        self.max_power_dict = dict() 
        
        for turbine_name in self.turbine_names:
            # extract filterd data for a single turbine
            normal_temp_df = self.normal_df[self.normal_df.Wind_turbine_name == turbine_name].copy()
            if self.method == 'binning':
                # bin filtered data before interpolation
                binned_df = binning_func(normal_temp_df, self.windspeed_label, self.power_label, self.bin_interval)
                # create turbine-level interpolation function for estimating expected power
                f = interp1d(binned_df.windspeed_bin_median, binned_df.pwr_bin_mean, kind=self.kind, fill_value="extrapolate")
            elif self.method == 'autoML':
                print('AutoML method is yet to be released. Hence, reverting to binning method')
                # bin filtered data before interpolation
                binned_df = binning_func(normal_temp_df, self.windspeed_label, self.power_label, self.bin_interval)
                # create turbine-level interpolation function for estimating expected power
                f = interp1d(binned_df.windspeed_bin_median, binned_df.pwr_bin_mean, kind=self.kind, fill_value="extrapolate")
                
            self.pred_funcs_dict[turbine_name] = f
            self.max_power_dict[turbine_name] = binned_df.pwr_bin_mean.round().max()
            
        return self
        
       
    def predict(self, test_data):
        """
        Returns the same data as input with an additional expected power column
        """
        self.pred_df = test_data.copy()
        for turbine_name in self.turbine_names:
            test_temp_df = self.pred_df[self.pred_df[self.turbine_label] == turbine_name]
            test_temp_index = test_temp_df.index
            self.pred_df.loc[test_temp_index, 'expected_power'] = self.pred_funcs_dict[turbine_name](test_temp_df[self.windspeed_label])
            
            # post process expected power estimations to not exceed maximum value in training data
            self.pred_df.loc[test_temp_index, 'expected_power'] = self.pred_df.loc[test_temp_index,
                                                                                   'expected_power'].clip(upper=self.max_power_dict[turbine_name])

        self.pred_df['expected_power'].clip(0, inplace=True)
         
        return self.pred_df

       
if __name__ == "__main__":
    
    from sklearn.metrics import mean_absolute_error
    
    train_df = pd.read_csv(r'examples\datasets\training_data.zip')
    
    test_df = pd.read_csv(r'examples\datasets\test_data.zip')
    
    power_model = ExpectedPower(turbine_label='Wind_turbine_name', windspeed_label='Ws_avg',
                                power_label='P_avg', method='binning', kind='cubic')
    
    power_model.fit(train_df)
    
    predictions = power_model.predict(test_df)
    
    print('MAE:', mean_absolute_error(predictions['P_avg'], predictions['expected_power']))
    
    print('Prediction data', predictions.head())