from distutils.core import setup

setup(
    name = 'scada_data_analysis',
    packages = ['scada_data_analysis'],
    version = 'v1.0.0a',  
    description = 'This version features a power curve filtering\
                   module that takes in raw SCADA data from multiple wind turbines\
                   and returns two subsets of the original dataset namely the normal\
                   and abnormal operations data',
    author = 'Abiodun Olaoye',
    author_email = 'abiodunolaoye8@gmail.com',
    url = 'https://github.com/abbey2017/wind-energy-analytics',
    download_url = 'https://github.com/abbey2017/wind-energy-analytics/releases/tag/v1.0.0',
    keywords = ['scada-data-filtering', 'wind-energy'],
    classifiers = [],
)
