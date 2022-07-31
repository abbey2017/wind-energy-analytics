"""
This is a function for calculating the average power per wind speed bin for a given turbine
"""

# Import relevant library
import pandas as pd

def binning_func(self, turbine_data):
    """
    Bins wind speed into group of values using bin_interval
    
    turbine_data: pandas dataframe containing windspeed and power columns
    
    Returns: Median wind speed, average and standard deviation of produced power for each bin
    """
    turb_df = turbine_data.copy()
    max_windspeed = int(max(turb_df[self.windspeed_label]))
    
    windspeed_bins = pd.IntervalIndex.from_tuples([(round(self.bin_interval*a, 2),
                                                    round((self.bin_interval*a)+self.bin_interval, 2))\
                                                        for a in range(0, 2*max_windspeed+1)])
    
    turb_df.loc[:, 'windspeed_bin'] = pd.cut(turb_df[self.windspeed_label], bins=windspeed_bins)
    
    binned_turb_df = turb_df.groupby('windspeed_bin', as_index=False)[[self.windspeed_label,
                                                                        self.power_label]].agg({self.windspeed_label: 'median',
                                                                        self.power_label: ['mean', 'std']},
                                                                        as_index=False).dropna(subset=[(self.power_label,
                                                                        'mean')]).fillna({(self.power_label,
                                                                                            'std'): 0}).reset_index(drop=True)
    
    binned_turb_df.columns = ['windspeed_bin', 'windspeed_bin_median', 'pwr_bin_mean', 'pwr_bin_std']
    
    return binned_turb_df