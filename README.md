### wind-energy-analytics
Curating physics-guided data-driven solutions for the wind energy industry

### Current Modules
- Iterative power curve filter (returns normal and abnormal datapoints)

### Filtering Module Usage
```
from scada_data_analysis.modules.power_curve_preprocessing import PowerCurveFiltering

pc_filter = PowerCurveFiltering(turbine_label='Wind_turbine_name', windspeed_label='Ws_avg',
                                power_label='P_avg', data=df, cutin_speed=3, bin_interval=0.5,
                                z_coeff=2.5, filter_cycle=5, return_fig=True, image_path='..\images')

normal_df, abnormal_df = pc_filter.process()
```
