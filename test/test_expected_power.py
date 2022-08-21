"""
This script performs test on the power curve filtering module
"""
import sys
sys.path.extend(['.', '..'])

import unittest
import pandas as pd

from sklearn.metrics import mean_squared_error
from scada_data_analysis.modules.expected_power import ExpectedPower


class TestExpectedPower(unittest.TestCase):
    def setUp(self):
        try:
            self.df = pd.read_csv(r'examples/datasets/sample_df.csv')
        except:
            self.df = pd.read_csv(r'examples\datasets\sample_df.csv')
        
        # split data into train and test data
        self.train_df = self.df[:38000].reset_index(drop=True)
        self.test_df = self.df[38000:].reset_index(drop=True)
       
    def run_calculations(self, interp_kind):
        self.power_model = ExpectedPower(turbine_label='Wind_turbine_name', windspeed_label='Ws_avg',
                                         power_label='P_avg', method='binning', kind=interp_kind)
        self.power_model = self.power_model.fit(self.train_df)
        self.pred_df = self.power_model.predict(self.test_df)
        self.pred_metric = round(mean_squared_error(self.pred_df['P_avg'],
                                                    self.pred_df['expected_power'], squared=False), 6)
        return self.pred_metric
    
    def test_expected_power_results(self):
        
        computed_score = self.run_calculations('linear')
        expected_score = 80.904492
        
        # test returned shape of subsets
        assert computed_score == expected_score, "Returned score of expected power estimation does not match expected score"
   
    def tearDown(self) -> None:
        pass
        
    
if __name__ == '__main__':
    unittest.main()
