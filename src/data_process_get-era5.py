# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 10:14:45 2025

@author: zpb4
"""

import pandas as pd
import numpy as np
#import xarray as xr
import cdsapi
import sys

idx = int(sys.argv[1])-1
#idx=1

short_names = ['t2m','d2m','u10','v10','u10n','v10n','tp','tcc']
yr_st = 2025
yr_en = 2025

yrs = yr_st + np.arange(yr_en-yr_st+1)

#grid boxes covering Cannonsville reservoir
nth = 42.25
sth = 42.0
wst = -75.5
est = -75.0

#required variables
var_names = [
     "10m_u_component_of_wind",
     "10m_v_component_of_wind",
     "2m_dewpoint_temperature",
     "2m_temperature",
     "total_precipitation",
     "total_cloud_cover"
 ]

#extract daily values from the ERA5 CDS API
for i in enumerate(yrs):
  output_folder = './raw_data/%s_%s.nc' %(var_names[idx],str(i[1]))
  dataset = "derived-era5-single-levels-daily-statistics"
  request = {
            "product_type": "reanalysis",
            "variable": [
                var_names[idx]
                ],
            "year": str(i[1]),
            "month": [
                "01", "02", "03",
                "04", "05", "06",
                "07", "08", "09",
                "10", "11", "12"
                ],
            "day": [
                "01", "02", "03",
                "04", "05", "06",
                "07", "08", "09",
                "10", "11", "12",
                "13", "14", "15",
                "16", "17", "18",
                "19", "20", "21",
                "22", "23", "24",
                "25", "26", "27",
                "28", "29", "30",
                "31"
                ],
            "daily_statistic": "daily_mean",
            "time_zone": "utc+00:00",
            "frequency": "6_hourly",
            "area": [nth, wst, sth, est]
            }

  client = cdsapi.Client()
  #client.retrieve(dataset, request).download()
  client.retrieve(dataset,request,output_folder)


#------------------------------------------------END-----------------------------------------