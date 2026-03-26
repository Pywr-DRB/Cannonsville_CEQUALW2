# CE-QUAL-W2 model 
This repository houses the executables and data required to run the CE-QUAL-W2 hydrodynamics model (version 4.5) for Cannonsville Reservoir, NY. This README file provides a high-level overview of the contents of the repository, including data-processing of the CE-QUAL-W2 inputs, setting up the CE-QUAL-W2 model, running the model, and analyzing the output via raw output data and the W2 post-processor tool. 
    
Consult the conceptual discussion of the CE-QUAL-W2 model on the Waterprogramming Blog Post [here](https://waterprogramming.wpcomstaging.com/2025/10/16/ce-qual-w2-overview-and-application/) and associated GitHub repo [here](https://github.com/zpb4/ce-qual-w2_waterprogramming_example). CE-QUAL-W2 will be referred to as 'W2' below for brevity.

## Dependencies
All the required executables for CE-QUAL-W2 (version 4.5) are included in the root directory of this repo, including the W2 preprocessor (preW2-v45_64.exe), the W2 model (w2_v45_64.exe), and the W2 postprocessor (W2_Post3.exe). The data-processing is Python-based and requires the following dependencies:
- Numpy, Pandas, xarray
- cdsapi (ERA5 extraction)

## Workflow
All required raw input data for Cannonsville reservoir is archived in the 'data' subdirectory. The './src/data_processing.py' converts the raw files in this subdirectory to the formatted inflow, outflow, inflow-temperature, and meteorological inputs for the W2 model. The meteorological inputs were derived from ERA5 reanalysis; the 'data_process_get-era5.py' script retrieves the data from the Copernicus server and the 'data_process_era5-ncdf.py' script processes the ERA5 data into a single timeseries file for the Cannonsville domain.  Synopsis of W2 required inputs:
- Bathymetry: bathymetry .csv file (Bath_CAN.csv) in the 'bathymetry' subdirectory
- Meteorology: W2 requires air temp, dewpoint temp, wind speed, wind direction, and cloud cover to run. These data were derived from ERA5 and are archived in the meteorological input file (met.csv) in the 'met' subdirectory
- Inflow: The 2 inflow points for Cannonsville Reservoir (Trout Creek 'Tcrk', West Branch Delaware River 'Wdel') have separate inflow files in the inflow subdirectory 'inflows', which are named 'qin_Wdel_br1, qin_Tcrk_br2'. These files are derived from the aggregated Cannonsville inflow which has been partitioned by mean inflow percentage to Trout Creek and the West Delaware River.
- Inflow temperature: Inflow temperature files are archived as for Inflow but using 'tin_' instead of 'qin_'. Since only the W. Delaware has a temp gage, the same temperature is used for both inflow sources.
- Outflow: The outflows for Cannonsville reservoir are the specified releases. The current configuration has all releases coming out of the main outlet that draws from the lower portion of the reservoir, although there is a spillway outlet specified in the W2 control file. The W2 control file understands the release location based on the order of the 'QOUT' specifications in the outflow 'otflow_br1.csv' file.
