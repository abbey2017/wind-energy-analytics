"""
This module applies iterative filtering to scada data.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt


class PowerCurveFiltering:
    """
    This class returns two subsets of the original SCADA data representing normal and abnormal operations
    """
    
    def __init__(self, turbine_label, windspeed_label, power_label, data=None, cut_in_speed=3,
                 bin_interval=0.5, z_coeff=2, filter_cycle=5, return_fig=False, image_path=None):
        """
        turbine_label: column name of unique turbine identifier
        windspeed_label: column name of wind speed
        power_label: column name of active power
        data: pandas dataframe of scada data
        cut_in_speed: cut in speed of turbine
        bin_interval: Wind speed bin interval
        z_coeff: threshold of standard deviation used in filter within which operational data is considered normal
        filter_cycle: number of times to pass scada data through filter
        return_fig: if true, module returns power curve plot in addition to filtered datasets
        image_path: used only if return_fig is True
        """
        self.turbine_label = turbine_label
        self.windspeed_label = windspeed_label
        self.power_label = power_label 
        self.data = data
        self.cut_in_speed = cut_in_speed
        self.bin_interval = bin_interval
        self.z_coeff = z_coeff
        self.filter_cycle = filter_cycle
        self.return_fig = return_fig
        self.image_path = image_path
        
    def remove_downtime_events(self):
        """
        Filters out downtime events from SCADA data 
        """
        self.no_dt_df =  self.data[~((self.data[self.power_label] <= 1) &\
                                     (self.data[self.windspeed_label] >= self.cut_in_speed))]
        
    def remove_fault_events_per_turbine(self):
        """
        Filters out data points with unrealistically low power output at moderately high wind speeds.
        This step also helps improve filtering procedure by reducing noise in data.
        """
        max_power = self.no_dt_per_turbine_df[self.power_label].max()
        
        self.no_dt_per_turbine_df = self.no_dt_per_turbine_df.drop(self.no_dt_per_turbine_df[((self.no_dt_per_turbine_df[self.power_label] < 0.9*max_power) &\
                                                                                             (self.no_dt_per_turbine_df[self.windspeed_label] > 4.5*self.cut_in_speed))].index)
        
    def process(self):
        """
        Runs the different methods and functions that processes the scada data
        """
        self.remove_downtime_events()
        turbine_names = self.data[self.turbine_label].unique()
        
        filtered_ind_list = []
        
        for turbine_name in turbine_names:
            self.no_dt_per_turbine_df = self.no_dt_df[self.no_dt_df[self.turbine_label] == turbine_name]
                                                      
            # Remove faulty events from remaining non-downtime data
            self.remove_fault_events_per_turbine()
            
            filtered_ind_list.append(self.secondary_filter())
            
        normal_ind_list = sum(filtered_ind_list, [])
        
        abnormal_ind_list = list(set(self.data.index.tolist()).difference(set(normal_ind_list)))
    
        assert len(self.data.index.tolist()) == len(normal_ind_list) + len(abnormal_ind_list)

        normal_df = self.data.iloc[normal_ind_list]

        abnormal_df = self.data.iloc[abnormal_ind_list]
        
        if self.return_fig:
            self.normal_df = normal_df.copy()
            self.abnormal_df = abnormal_df.copy()
            
            self.normal_df.loc[:, 'Abnormal'] = 'No'
            self.abnormal_df.loc[:, 'Abnormal'] = 'Yes'
            
            self.processed_data = pd.concat([self.normal_df, self.abnormal_df])
            
            if not os.path.exists(self.image_path):
                os.mkdir(self.image_path)
            
            for turbine_name in turbine_names:
                turbine_data = self.processed_data[self.processed_data[self.turbine_label] == turbine_name]

                plt.figure(figsize=(18,6))
                plt.scatter(x=self.windspeed_label, y=self.power_label, s=6, data=turbine_data, c=turbine_data['Abnormal'].map({'No':'blue', 'Yes':'orange'}))
                plt.title(f"Operational power curve for turbine {turbine_name}", fontsize=16)
                plt.xlabel("Wind Speed", fontsize=14)
                plt.ylabel("Power", fontsize=14)
                plt.xticks(fontsize=14)
                plt.yticks(fontsize=14)
                fname = fr"{self.image_path}\{turbine_name}_pc.png"
                plt.savefig(fname)
            
        return normal_df, abnormal_df

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

    def secondary_filter(self):
        """
        Filters the turbine data using provided threshold (z_coeff)
        Returns: Median wind speed, average and standard deviation of produced power for each bin
        """

        no_dt_per_turbine_df = self.no_dt_per_turbine_df.reset_index().copy()
        
        if 'windspeed_bin' not in no_dt_per_turbine_df.columns:
            max_windspeed = int(max(no_dt_per_turbine_df[self.windspeed_label]))
            windspeed_bins = pd.IntervalIndex.from_tuples([(round(self.bin_interval*a, 2),
                                                            round((self.bin_interval*a)+self.bin_interval, 2))\
                                                                for a in range(0, 2*max_windspeed+1)])
            no_dt_per_turbine_df.loc[:, 'windspeed_bin'] = pd.cut(no_dt_per_turbine_df[self.windspeed_label], bins=windspeed_bins)
            
        if self.filter_cycle == 0:
            print("Number of iterative steps cannot be less than 1, filter_cycle set to 1!")
            self.filter_cycle = 1
        
        for _ in range(int(self.filter_cycle)):
            
            binned_turb_df = self.binning_func(no_dt_per_turbine_df)
            
            if set(no_dt_per_turbine_df.columns).issuperset(set(['windspeed_bin_median', 'pwr_bin_mean', 'pwr_bin_std'])):
                no_dt_per_turbine_df.drop(['windspeed_bin_median', 'pwr_bin_mean', 'pwr_bin_std'], axis=1, inplace=True)
                
            no_dt_per_turbine_df = pd.merge(no_dt_per_turbine_df, binned_turb_df, how='left', on='windspeed_bin')
            
            no_dt_per_turbine_df.loc[:, 'pwr_low_thresh'] = no_dt_per_turbine_df['pwr_bin_mean'] - self.z_coeff*no_dt_per_turbine_df['pwr_bin_std']
            no_dt_per_turbine_df.loc[:, 'pwr_low_thresh'] = no_dt_per_turbine_df['pwr_low_thresh'].apply(lambda x: 0 if x < 0 else x)

            no_dt_per_turbine_df.loc[:, 'pwr_high_thresh'] = no_dt_per_turbine_df['pwr_bin_mean'] + self.z_coeff*no_dt_per_turbine_df['pwr_bin_std']
            no_dt_per_turbine_df.loc[:, 'pwr_high_thresh'] = no_dt_per_turbine_df['pwr_high_thresh'].apply(lambda x: 0 if x < 0 else x)

            no_dt_per_turbine_df = no_dt_per_turbine_df[(no_dt_per_turbine_df[self.power_label] > no_dt_per_turbine_df.pwr_low_thresh) &\
                                   (no_dt_per_turbine_df[self.power_label] < no_dt_per_turbine_df.pwr_high_thresh) |\
                                   (no_dt_per_turbine_df[self.windspeed_label] < self.cut_in_speed)]
        
        return no_dt_per_turbine_df['index'].tolist()
    
if __name__ == "__main__":
    df = pd.read_csv(r'..\..\examples\datasets\la-haute-borne-data-2017-2020.zip', sep=';')
    
    pc_filter = PowerCurveFiltering(turbine_label='Wind_turbine_name', windspeed_label='Ws_avg',
                                    power_label='P_avg', data=df, cut_in_speed=3, bin_interval=0.5,
                                    z_coeff=2.5, filter_cycle=5, return_fig=True, image_path=r'..\..\examples\images')
    normal_df, abnormal_df = pc_filter.process()
    print('Normal Operations Data', normal_df.head())
    print('Abnormal Operations Data', abnormal_df.head())
    