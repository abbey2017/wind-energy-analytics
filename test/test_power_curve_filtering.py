"""
This script performs test on the power curve filtering module
"""
import sys
sys.path.extend(['.', '..'])

import unittest
import pandas as pd

from scada_data_analysis.modules.power_curve_preprocessing import PowerCurveFiltering


class TestPowerCurveFiltering(unittest.TestCase):
    def setUp(self):
        try:
            self.df = pd.read_csv(r'examples/datasets/test_df.csv')
        except:
            self.df = pd.read_csv(r'examples\datasets\test_df.csv')
        
        self.pc_filter = PowerCurveFiltering(turbine_label='Wind_turbine_name', windspeed_label='Ws_avg', power_label='P_avg', data=self.df, 
                                             cut_in_speed=3, bin_interval=0.5, z_coeff=2.5, filter_cycle=5, return_fig=False)
        
        self.normal_df, self.abnormal_df = self.pc_filter.process()

    def test_power_curve_filtering_results(self):
        
        computed_shape = pd.concat([self.normal_df, self.abnormal_df]).shape
        
        expected_normal_indices = [0, 2, 3, 5, 6, 7, 8, 9, 10, 11]
        expected_abnormal_indices = [1, 8193, 40963, 4, 32773, 32776, 49160, 16397, 40974, 49169]
        computed_normal_indices = self.normal_df.index.tolist()
        computed_abnormal_indices = self.abnormal_df.index.tolist()
        
        # Test returned shape of subsets
        assert computed_shape == self.df.shape, "Returned shape of output data does not match input data"
        
        # Test results of normal operating conditions
        assert  set(expected_normal_indices).issubset(set(computed_normal_indices)), "Expected normal operating data not in computed results"
        
        # Test results for abnormal operating conditions
        assert set(expected_abnormal_indices).issubset(set(computed_abnormal_indices)), "Expected abnormal operating data not in computed results"
        
    def tearDown(self) -> None:
        pass
        
    
if __name__ == '__main__':
    unittest.main()
