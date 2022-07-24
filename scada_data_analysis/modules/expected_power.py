"""
This module is used to estimate the expected power of a wind turbine generator.
"""
import pandas as pd

from scipy.interpolate import interp1d
from scada_data_analysis.modules.power_curve_preprocessing import PowerCurveFiltering as pcf

class BinningMethod:
    def __init__(self, turbine_label, windspeed_label, power_label, data=None, cut_in_speed=3,
                 bin_interval=0.5, z_coeff=2, filter_cycle=5, method='linear') -> None:
        """
        turbine_label: column name of unique turbine identifier
        windspeed_label: column name of wind speed
        power_label: column name of active power
        data: pandas dataframe of scada data
        cut_in_speed: cut in speed of turbine
        bin_interval: Wind speed bin interval
        z_coeff: threshold of standard deviation used in filter within which operational data is considered normal
        filter_cycle: number of times to pass scada data through filter
        method: method used to calculate the expected power. Available methods are: 'linear', 'quadratic' and 'cubic'.
        Quadratic and cubic methods use spline interpolation of second and third order respectively.
        """
        self.turbine_label = turbine_label
        self.windspeed_label = windspeed_label
        self.power_label = power_label 
        self.data = data
        self.cut_in_speed = cut_in_speed
        self.bin_interval = bin_interval
        self.z_coeff = z_coeff
        self.filter_cycle = filter_cycle
        self.method = method
        
        # Initialize power curve processing class
        pc_filter = pcf.PowerCurvePreprocessing(self.turbine_label, self.windspeed_label, self.power_label,
                                                self.data, self.cut_in_speed, self.bin_interval, self.z_coeff,
                                                self.filter_cycle, self.method)

        # Get data points during normal operating conditions
        normal_df, _ = pc_filter.process()
        
        # For each turbine, get statistics of the wind speed bin and active power
        