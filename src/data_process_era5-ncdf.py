# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 10:14:45 2025

@author: zpb4
"""

import pandas as pd
import numpy as np
import xarray as xr
import sys

short_names = ['u10','v10','d2m','t2m','tp','tcc']
yr_st = 1940
yr_en = 2025

yrs = yr_st + np.arange(yr_en-yr_st+1)

nth = 42.25
sth = 42.0
wst = -75.5
est = -75.0

var_names = [
     "10m_u_component_of_wind",
     "10m_v_component_of_wind",
     "2m_dewpoint_temperature",
     "2m_temperature",
     "total_precipitation",
     "total_cloud_cover"
 ]

for k in range(len(var_names)):
    output_folder = './raw_data/%s_%s.nc' %(var_names[k],yrs[0])
    da = xr.open_dataset(output_folder, engine="netcdf4")

    dat = da[short_names[k]].values
    out = np.mean(dat,axis=(1,2))

    for i in range(1,len(yrs)):
        output_folder = './raw_data/%s_%s.nc' %(var_names[k],yrs[i])
        da = xr.open_dataset(output_folder, engine="netcdf4")

        dat_add = da[short_names[k]].values
        out_add = np.mean(dat_add,axis=(1,2))
        dat = np.concat((dat,dat_add),axis=0)
        out = np.concat((out,out_add),axis=0)
    
    np.savez('./data/%s_N%s-%s_E%s-%s_%s-%s.npz' %(var_names[k],sth,nth,wst,est,yrs[0],yrs[-1]),arr=dat)
    np.savez('./data/%s_area-mean_N%s-%s_E%s-%s_%s-%s.npz' %(var_names[k],sth,nth,wst,est,yrs[0],yrs[-1]),arr=out)


sd_hist = '1940-01-01'
ed_hist = '2025-12-31'

jday_ref = '1940-01-01'

era5_dtg = pd.date_range(sd_hist,ed_hist,freq='D')
hist_dtg = pd.date_range(sd_hist,ed_hist,freq='D')

jday_hist = len(pd.date_range(jday_ref,sd_hist,freq='D'))

tdew = np.load('./data/%s_area-mean_N%s-%s_E%s-%s_%s-%s.npz' %(var_names[2],sth,nth,wst,est,yrs[0],yrs[-1]))['arr']
tdew_df = pd.Series(tdew,index=era5_dtg)
tdew_hist = tdew_df.loc[pd.date_range(sd_hist,ed_hist,freq='D')] - 273.15

tair = np.load('./data/%s_area-mean_N%s-%s_E%s-%s_%s-%s.npz' %(var_names[3],sth,nth,wst,est,yrs[0],yrs[-1]))['arr']
tair_df = pd.Series(tair,index=era5_dtg)
tair_hist = tair_df.loc[pd.date_range(sd_hist,ed_hist,freq='D')] - 273.15

precip = np.load('./data/%s_area-mean_N%s-%s_E%s-%s_%s-%s.npz' %(var_names[4],sth,nth,wst,est,yrs[0],yrs[-1]))['arr']
precip_df = pd.Series(precip,index=era5_dtg)
precip_hist = precip_df.loc[pd.date_range(sd_hist,ed_hist,freq='D')] 

uwnd = np.load('./data/%s_area-mean_N%s-%s_E%s-%s_%s-%s.npz' %(var_names[0],sth,nth,wst,est,yrs[0],yrs[-1]))['arr']
uwnd_df = pd.Series(uwnd,index=era5_dtg)
uwnd_hist = uwnd_df.loc[pd.date_range(sd_hist,ed_hist,freq='D')]

vwnd = np.load('./data/%s_area-mean_N%s-%s_E%s-%s_%s-%s.npz' %(var_names[1],sth,nth,wst,est,yrs[0],yrs[-1]))['arr']
vwnd_df = pd.Series(vwnd,index=era5_dtg)
vwnd_hist = vwnd_df.loc[pd.date_range(sd_hist,ed_hist,freq='D')]

clcov = np.load('./data/%s_area-mean_N%s-%s_E%s-%s_%s-%s.npz' %(var_names[5],sth,nth,wst,est,yrs[0],yrs[-1]))['arr']
clcov_df = pd.Series(clcov,index=era5_dtg)
clcov_hist = clcov_df.loc[pd.date_range(sd_hist,ed_hist,freq='D')] * 10

#wind speed & direction calcs
wind_spd_hist = np.sqrt(uwnd_hist**2 + vwnd_hist**2)
#meteorological wind direction in rads (phi)
phi_hist = np.atan2(uwnd_hist/wind_spd_hist, vwnd_hist/wind_spd_hist) + np.pi


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#output to full length of potential historical data (1/1/1940 - 12/31/2025)
data = {'JDAY':np.arange(len(hist_dtg)) + jday_hist,'TAIR':round(tair_hist,1),'TDEW':round(tdew_hist,1),'WIND':round(wind_spd_hist,2),'PHI':round(phi_hist,2),'CLOUD':round(clcov_hist,1)}
df = pd.DataFrame(data)

data2 = {'JDAY':hist_dtg,'TAIR':round(tair_hist,1),'TDEW':round(tdew_hist,1),'WIND':round(wind_spd_hist,2),'PHI':round(phi_hist,2),'CLOUD':round(clcov_hist,1)}
df2 = pd.DataFrame(data2)

empty_rows = 2
empty_data = {col: ['' for _ in range(empty_rows)] for col in df.columns}
empty_df = pd.DataFrame(empty_data)
# Concatenate the original DataFrame with the empty DataFrame
df_out = pd.concat([empty_df,df], ignore_index=True)
df_out.iloc[1,:] = df.columns

df_out.to_csv('./data/met_cannonsville-era5_hist.csv',index=False,header=['$%s to %s  ERA5 daily-mean N%s-%s_E%s-%s' %(str(hist_dtg[0])[:10],str(hist_dtg[-1])[:10],sth,nth,wst,est),'','','','',''])

df_out2 = pd.concat([empty_df,df2], ignore_index=True)
df_out2.iloc[1,:] = df.columns
df_out2.to_csv('./data/met_cannonsville-era5_hist-dates.csv',index=False,header=['$%s to %s ERA5 daily-mean N%s-%s_E%s-%s' %(str(hist_dtg[0])[:10],str(hist_dtg[-1])[:10],sth,nth,wst,est),'','','','',''])


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#output precip data
data = {'Date':hist_dtg ,'PRECIP':precip_hist}
df = pd.DataFrame(data)
df.to_csv('./data/precip_era5-hist_%s-%s.csv' %(str(hist_dtg[0])[:10],str(hist_dtg[-1])[:10]),index=False)


#------------------------------------------------END-----------------------------------------