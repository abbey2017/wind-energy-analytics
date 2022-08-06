This library helps lower the entry barrier for domain experts
in the wind energy industry to leverage advanced analytics and methodologies
developed in related scientific research.

Modules are implemented for different routine and non-routine analysis of time series
data collected from operating wind turbines. Practicing wind engineers and analysts
can build on fundamental modules as part of a larger project development.

### Library installation
- Clone the github repo to have access to example notebooks and public data.
- Next, pip install the library

```
# Clone github repo
git clone https://github.com/abbey2017/wind-energy-analytics.git

# Pip install library
pip install scada-data-analysis
```

### Current modules
- Iterative power curve filter (returns normal and abnormal datapoints)

### Usage of power curve filter
```
import pandas as pd

from scada_data_analysis.modules.power_curve_preprocessing import PowerCurveFiltering

# Load turbine scada data
df = pd.read_csv('path\to\data')

# Instantiate power curve filtering class
pc_filter = PowerCurveFiltering(turbine_label='Wind_turbine_name', windspeed_label='Ws_avg',
                                power_label='P_avg', data=df, cut_in_speed=3, bin_interval=0.5,
                                z_coeff=2.5, filter_cycle=5, return_fig=True, image_path='..\images')

# Process raw scada data
normal_df, abnormal_df = pc_filter.process()
```
