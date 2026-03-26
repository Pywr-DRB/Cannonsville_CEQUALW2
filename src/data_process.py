# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 21:08:43 2025

@author: zpb4
"""
import pandas as pd
import numpy as np
import xarray as xr
import sys
import calendar

cfs_to_m3s = 0.028316847
mgd_to_m3d = 3785.4118
mgd_to_m3s = mgd_to_m3d / (24*60*60)
ft_to_m = 0.3048
jday_ref = '1940-01-01'

print(np.array([1053,1107,1141])*ft_to_m)

#...............................................................
#load required W2 model data
#ERA5 meteorological data (pre-processed to match CE-QUAL-W2 convention)
met = pd.read_csv('./data/met_cannonsville-era5_hist-dates.csv',index_col=0,skiprows=2,parse_dates=True)
print(met.index[0],met.index[-1])
#Aggregated Cannonsville inflow/outflow in millions of gallons per day
inf_otflow = pd.read_csv('./data/cannonsville_inflow_outflow_mgd.csv',index_col=0,header=0,parse_dates=True)
print(inf_otflow.index[0],inf_otflow.index[-1])
#Aggregated Cannonsville inflow/outflow/storage in millions of gallons per day
inf_otflow_store = pd.read_csv('./data/cannonsville_data.csv',index_col=0,header=0,parse_dates=True)
print(inf_otflow_store.index[0],inf_otflow_store.index[-1])
#Main W Branch DE river temps
Wdel_temp = pd.read_csv('./data/WBranch_DERiver_ USGS-01423000_temp_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(Wdel_temp.index[0],Wdel_temp.index[-1]) #date sequences are reversed in USGS data


#...............................................................
#load additional data
#Main W Branch DE river inflows in cfs
Wdel_inflow = pd.read_csv('./data/WBranch_DERiver_ USGS-01423000_inflow-cfs_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(Wdel_inflow.index[0],Wdel_inflow.index[-1]) #date sequences are reversed in USGS data
#Trout creek inflows in cfs
Tcrk_inflow = pd.read_csv('./data/TroutCreek_USGS-0142400103_inflow-cfs_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(Tcrk_inflow.index[0],Tcrk_inflow.index[-1]) #date sequences are reversed in USGS data
#Cannonsville outflow temp in deg C
otflow_temp = pd.read_csv('./data/nwis_Cannonsville_degC_mgd.csv',index_col=0,header=0,parse_dates=True)
print(otflow_temp.index[0],otflow_temp.index[-1])
#Cannonsville outflow temp in deg C at Stilesville
CanSti_otflow_temp = pd.read_csv('./data/Cannonsville_Stilesville-outflow_USGS-01425000_temp_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(CanSti_otflow_temp.index[0],CanSti_otflow_temp.index[-1])
#Cannonsville outflow temp in deg C at Stilesville
CanSti_otflow = pd.read_csv('./data/Cannonsville_Stilesville-outflow_USGS-01425000_outflow_cfs_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(CanSti_otflow.index[0],CanSti_otflow.index[-1])
#Cannonsville reservoir temp at 1053'
CanRes_temp_1053 = pd.read_csv('./data/Cannonsville_USGS-01423910_reservoir-temp_1053ft_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(CanRes_temp_1053.index[0],CanRes_temp_1053.index[-1])
#Cannonsville reservoir temp at 1053'
CanRes_temp_1107 = pd.read_csv('./data/Cannonsville_USGS-01423910_reservoir-temp_1107ft_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(CanRes_temp_1107.index[0],CanRes_temp_1107.index[-1])
#Cannonsville reservoir temp at 1053'
CanRes_temp_1144 = pd.read_csv('./data/Cannonsville_USGS-01423910_reservoir-temp_1144ft_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(CanRes_temp_1144.index[0],CanRes_temp_1144.index[-1])
#Cannonsville reservoir elevation in ft
CanRes_elev = pd.read_csv('./data/Cannonsville_USGS-01423910_reservoir-elevation_ft_daily-mean.csv',index_col='time',header=0,parse_dates=True)
print(CanRes_elev.index[0],CanRes_elev.index[-1])

def water_day(d, is_leap_year):
    # Convert the date to day of the year
    day_of_year = d.timetuple().tm_yday
    
    # For leap years, adjust the day_of_year for dates after Feb 28
    if is_leap_year and day_of_year > 59:
        day_of_year -= 1  # Correcting the logic by subtracting 1 instead of adding
    
    # Calculate water day
    if day_of_year >= 274:
        # Dates on or after October 1
        dowy = day_of_year - 274
    else:
        # Dates before October 1
        dowy = day_of_year + 91  # Adjusting to ensure correct offset
    
    return dowy

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Process core W2 input data
#arrange date/time indices
st_date = max(met.index[0],inf_otflow_store.index[0],Wdel_temp.index[-1])
en_date = min(met.index[-1],inf_otflow_store.index[-1],Wdel_temp.index[0])
en_date = '2023-12-31'
print(st_date,en_date)

inf_dtg = pd.date_range(st_date,en_date,freq='D')
jday = len(pd.date_range(jday_ref,inf_dtg[0],freq='D'))

#inflow/outflow data
inf_otf_sset = inf_otflow_store[(inf_otflow_store.index >= st_date) & (inf_otflow_store.index <= en_date)]
inflow = inf_otf_sset['sim_inflow_mgd'] * mgd_to_m3s
outflow = inf_otf_sset['obs_release_mgd'] * mgd_to_m3s
#outflow = inf_otf_sset['sim_total_release_mgd'] * mgd_to_m3s
add_vec = np.zeros_like(outflow)
outflow = outflow + 2

#Wdel and Trout Creek inflows for proportioning
Wdel_inf_sset = Wdel_inflow[(Wdel_inflow.index >= st_date) & (Wdel_inflow.index <= en_date)]
Wdel_inf = Wdel_inf_sset['value'].values
Tcrk_inf_sset = Tcrk_inflow[(Tcrk_inflow.index >= st_date) & (Tcrk_inflow.index <= en_date)]
Tcrk_inf = Tcrk_inf_sset['value'].values
prop_Wdel = np.mean(Wdel_inf) / (np.mean(Wdel_inf) + np.mean(Tcrk_inf))
prop_Tcrk = np.mean(Tcrk_inf) / (np.mean(Wdel_inf) + np.mean(Tcrk_inf))

#meteorology
met_sset = met[(met.index >= st_date) & (met.index <= en_date)]

#inflow temperature
inf_temp_flip = Wdel_temp.iloc[::-1]
inf_temp_sset = inf_temp_flip[(inf_temp_flip.index >= st_date) & (inf_temp_flip.index <= en_date)]
#identify missing dates and reindex
missing_dates = inf_dtg.difference(inf_temp_flip.index)
inf_temp_reindex = inf_temp_flip.reindex(inf_dtg)
#extract temperature values and replace nan with mean values for same dowy
inf_temp_vals = inf_temp_reindex['value'].values
dowy = np.array([water_day(d,calendar.isleap(d.year)) for d in inf_temp_reindex.index])
for i in range(len(inf_temp_vals)):
    if np.isnan(inf_temp_vals[i]) == True:
        wdays = np.where(dowy==dowy[i])
        tmn = np.nanmean(inf_temp_vals[wdays])
        inf_temp_vals[i] = tmn
        
inflow_temp = pd.Series(inf_temp_vals)

#setup dataframes
inf_Wdel_br1 = {'JDAY':np.arange(len(inf_dtg)) + jday,'QIN':round(inflow * prop_Wdel,2)}
inf_Tcrk_br2 = {'JDAY':np.arange(len(inf_dtg)) + jday,'QIN':round(inflow * prop_Tcrk,2)}

inftemp_Wdel_br1 = {'JDAY':np.arange(len(inf_dtg)) + jday,'TIN':round(inflow_temp,2)}
inftemp_Tcrk_br2 = {'JDAY':np.arange(len(inf_dtg)) + jday,'TIN':round(inflow_temp,2)}

otf_br1 = {'JDAY':np.arange(len(inf_dtg)) + jday,'QOUT1':np.zeros(len(inf_dtg)), 'QOUT2':round(outflow,2)}

#output each data file to the correct repo and file format
#Br 1 inflows
inf_Wdel_br1_df = pd.DataFrame(inf_Wdel_br1)
empty_rows = 2
empty_data = {col: ['' for _ in range(empty_rows)] for col in inf_Wdel_br1_df.columns}
empty_df = pd.DataFrame(empty_data)
# Concatenate the original DataFrame with the empty DataFrame
df = pd.concat([empty_df,inf_Wdel_br1_df], ignore_index=True)
df.iloc[1,:] = inf_Wdel_br1_df.columns
df.to_csv('./inflow/qin_Wdel_br1.csv',index=False,header=['$%s to %s West Branch Delaware River inflows - m3/s (proportional estimate)' %(str(st_date)[:10],str(en_date)[:10]),''])

#Br 2 inflows
inf_Tcrk_br2_df = pd.DataFrame(inf_Tcrk_br2)
empty_rows = 2
empty_data = {col: ['' for _ in range(empty_rows)] for col in inf_Tcrk_br2_df.columns}
empty_df = pd.DataFrame(empty_data)
# Concatenate the original DataFrame with the empty DataFrame
df = pd.concat([empty_df,inf_Tcrk_br2_df], ignore_index=True)
df.iloc[1,:] = inf_Tcrk_br2_df.columns
df.to_csv('./inflow/qin_Tcrk_br2.csv',index=False,header=['$%s to %s Trout Creek inflows - m3/s (proportional estimate)' %(str(st_date)[:10],str(en_date)[:10]),''])

#Br 1 temps
inftemp_Wdel_br1_df = pd.DataFrame(inftemp_Wdel_br1)
empty_rows = 2
empty_data = {col: ['' for _ in range(empty_rows)] for col in inftemp_Wdel_br1_df.columns}
empty_df = pd.DataFrame(empty_data)
# Concatenate the original DataFrame with the empty DataFrame
df = pd.concat([empty_df,inftemp_Wdel_br1_df], ignore_index=True)
df.iloc[1,:] = inftemp_Wdel_br1_df.columns
df.to_csv('./inflow/tin_Wdel_br1.csv',index=False,header=['$%s to %s West Branch Delaware River inflow temp - degC' %(str(st_date)[:10],str(en_date)[:10]),''])

#Br 2 inflows
inftemp_Tcrk_br2_df = pd.DataFrame(inftemp_Tcrk_br2)
empty_rows = 2
empty_data = {col: ['' for _ in range(empty_rows)] for col in inftemp_Tcrk_br2_df.columns}
empty_df = pd.DataFrame(empty_data)
# Concatenate the original DataFrame with the empty DataFrame
df = pd.concat([empty_df,inftemp_Tcrk_br2_df], ignore_index=True)
df.iloc[1,:] = inftemp_Tcrk_br2_df.columns
df.to_csv('./inflow/tin_Tcrk_br2.csv',index=False,header=['$%s to %s Trout Creek inflow temp - degC (W Branch Delaware temps)' %(str(st_date)[:10],str(en_date)[:10]),''])

#Outflows
otf_br1_df = pd.DataFrame(otf_br1)
empty_rows = 2
empty_data = {col: ['' for _ in range(empty_rows)] for col in otf_br1_df.columns}
empty_df = pd.DataFrame(empty_data)
# Concatenate the original DataFrame with the empty DataFrame
df = pd.concat([empty_df,otf_br1_df], ignore_index=True)
df.iloc[1,:] = ['JDAY','QOUT','QOUT']
df.to_csv('./outflow/outflow_br1.csv',index=False,header=['$%s to %s Cannonsville outflow - m3s' %(str(st_date)[:10],str(en_date)[:10]),'',''])

#Meteorology
met_out = met_sset.reset_index(drop=True)
met_out.insert(0, "JDAY", np.arange(len(inf_dtg)) + jday)
empty_rows = 2
empty_data = {col: ['' for _ in range(empty_rows)] for col in met_out.columns}
empty_df = pd.DataFrame(empty_data)
# Concatenate the original DataFrame with the empty DataFrame
df = pd.concat([empty_df,met_out], ignore_index=True)
df.iloc[1,:] = met_out.columns
df.to_csv('./met/met.csv',index=False,header=['$%s to %s Cannonsville meteorology (ERA5)' %(str(st_date)[:10],str(en_date)[:10]),'','','','',''])


#-------------------------------------------------------------------------------------------------------------------------------------
#process other data for comparison purposes
#reservoir elevation
CanRes_elev_flip = CanRes_elev.iloc[::-1]
CanRes_elev_sset = CanRes_elev_flip[(CanRes_elev_flip.index >= st_date) & (CanRes_elev_flip.index <= en_date)]
#identify missing dates and reindex
missing_dates = inf_dtg.difference(CanRes_elev_flip.index)
CanRes_elev_reindex = CanRes_elev_flip.reindex(inf_dtg)
#extract temperature values and replace nan with mean values for same dowy
CanRes_elev_vals = CanRes_elev_reindex['value'].values
dowy = np.array([water_day(d,calendar.isleap(d.year)) for d in CanRes_elev_reindex.index])
for i in range(len(CanRes_elev_vals)):
    if np.isnan(CanRes_elev_vals[i]) == True:
        wdays = np.where(dowy==dowy[i])
        tmn = np.nanmean(CanRes_elev_vals[wdays])
        CanRes_elev_vals[i] = tmn
        
CanRes_elev_out = pd.Series(CanRes_elev_vals * ft_to_m)

#reservoir outflow temp
otflow_temp_sset = otflow_temp[(otflow_temp.index >= st_date) & (otflow_temp.index <= en_date)]
otflow_temp_vals = otflow_temp_sset['tavg_water_cannonsville']

#read in timeseries from W2 at the dam
w2_tsr = pd.read_csv('./tsr/tsr-dam_2_seg25.csv',index_col=0,header=0)
w2_elev = w2_tsr['ELWS(m)']
w2_temp = w2_tsr['T2(C)']


#plots
import matplotlib.pyplot as plt

spills = np.arange(len(inf_dtg))
idx_out = []
for i in range(len(spills)):
    if CanRes_elev_out[i] >= 350.52:
        idx_out.append(spills[i])

#compare elevation timeseries
plt.plot(inf_dtg,CanRes_elev_out,color='black',linewidth=2)
plt.plot(inf_dtg,w2_elev,color='green',linewidth=1.5,alpha=0.5)
plt.axhline(350.52,color='gray',linestyle='--',linewidth=1,alpha=0.5)
for i in range(len(idx_out)):
    plt.axvline(inf_dtg[idx_out[i]],color='red',linewidth=1,alpha=0.1)
plt.ylabel('Reservoir water elevation (m)')
plt.legend(['Obs','W2'],loc='lower left')
plt.show()
 
#compare outflow temperature timeseries
plt.plot(inf_dtg,otflow_temp_vals,color='black',linewidth=2)
plt.plot(inf_dtg,w2_temp,color='green',linewidth=1.5,alpha=0.5)
for i in range(len(idx_out)):
    plt.axvline(inf_dtg[idx_out[i]],color='red',linewidth=1,alpha=0.1)
plt.ylabel('Reservoir outflow temperature (m)')
plt.legend(['Obs','W2'],loc='upper left')
plt.show()


#############################################################END########################################