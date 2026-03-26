# CE-QUAL-W2 model 
This repository houses the executables and data required to run the CE-QUAL-W2 hydrodynamics model (version 4.5) for Cannonsville Reservoir, NY. This README file provides a high-level overview of the contents of the repository, including data-processing of the CE-QUAL-W2 inputs, setting up the CE-QUAL-W2 model, running the model, and analyzing the output via raw output data and the W2 post-processor tool. 
    
Consult the conceptual discussion of the CE-QUAL-W2 model on the Waterprogramming Blog Post [here](https://waterprogramming.wpcomstaging.com/2025/10/16/ce-qual-w2-overview-and-application/) and associated GitHub repo [here](https://github.com/zpb4/ce-qual-w2_waterprogramming_example). CE-QUAL-W2 will be referred to as 'W2' below for brevity.

## Dependencies
All the required executables for CE-QUAL-W2 (version 4.5) are included in the root directory of this repo, including the W2 preprocessor (preW2-v45_64.exe), the W2 model (w2_v45_64.exe), and the W2 postprocessor (W2_Post3.exe). The data-processing is Python-based and requires the following dependencies:
- Numpy, Pandas, xarray
- cdsapi (ERA5 extraction)

## Workflow
All required raw input data for Cannonsville reservoir is archived in the 'data' subdirectory. The './src/data_processing.py' converts the raw files in this subdirectory to the formatted inflow, outflow, inflow-temperature, and meteorological inputs for the W2 model. The meteorological inputs were derived from ERA5 reanalysis; the './src/data_process_get-era5.py' script retrieves the data from the Copernicus server and the './src/data_process_era5-ncdf.py' script processes the ERA5 data into a single timeseries file for the Cannonsville domain.  Synopsis of W2 required inputs:
- Bathymetry: bathymetry .csv file (Bath_CAN.csv) in the 'bathymetry' subdirectory. Cannonsville is modeled as two branches, with branch 1 containing the dam at its terminus and the West Delaware River at its upper end; branch 2 is the secondary branch that captures Trout Creek inflows and joins with branch 1 near the dam.
- Meteorology: W2 requires air temp, dewpoint temp, wind speed, wind direction, and cloud cover to run. These data were derived from ERA5 and are archived in the meteorological input file (met.csv) in the 'met' subdirectory
- Inflow: The 2 inflow points for Cannonsville Reservoir (Trout Creek 'Tcrk', West Branch Delaware River 'Wdel') have separate inflow files in the inflow subdirectory 'inflows', which are named 'qin_Wdel_br1, qin_Tcrk_br2'. These files are derived from the aggregated Cannonsville inflow which has been partitioned by mean inflow percentage to Trout Creek and the West Delaware River.
- Inflow temperature: Inflow temperature files are archived as for Inflow but using 'tin_' instead of 'qin_'. Since only the W. Delaware has a temp gage, the same temperature is used for both inflow sources.
- Outflow: The outflows for Cannonsville reservoir are the specified releases. The current configuration has all releases coming out of the main outlet that draws from the lower portion of the reservoir, although there is a spillway outlet specified in the W2 control file. The W2 control file understands the release location based on the order of the 'QOUT' specifications in the outflow 'outflow_br1.csv' file. The first QOUT column refers to the spillway elevation and the second QOUT column refers to the lower elevation release gate.
*Note: All W2 inputs must be specified by a Julian Day index which must match the settings in the W2 control file 
### Running the W2 model
The data have been prestaged and tested to be able to run the model upon cloning the directory. The W2 control file (w2_con_Cannonsville.xlsm) specifies all the model settings and input file names, output file names, output locations/elevations for timeseries, etc. There is some more discussion of this in the blog post linked above. The model is very sensitive to these settings and anything inconsistent in the model settings should be flagged by the pre-processing executable. To run the model:
1. Verify that the macro-enabled W2 control file has generated a 'w2_con.csv' file by hitting the big gray 'Export to CSV file' button at the top of the W2 control file.
2. Run the W2 preprocessor by double-clicking the 'preW2-v45_64.exe' icon. If everything is good, you may get some warnings, but should get 'Number of errors = 0' and 'Normal Termination' if everything is setup correctly. The preprocessor generates a pre.wrn output that you can look at for more detail on the warnings.
3. Run the W2 model by double-clicking the 'w2_v45_64.exe' icon. A window will pop up showing the simulation progress and a bunch of details about the simulation as it runs (e.g. water elevations, outflows, etc). If it runs to completion, it will output a number of files into predefined directories.
### Analyzing W2 outputs
This repo contains the W2 Postprocessing tool (W2_Post3.exe), which allows you to interrogate a large variety of information about the simulation via the saved .w2l file (e.g. CAN.w2l). Use of this tool is fairly intuitive after some familiarization.
The W2 model generates a number of other outputs. One of the most useful is the timeseries files, which are specified in the W2 control file (segment/layer specification), and output to the the 'tsr_' subdirectory. These timeseries files are tied to a specific section/depth of the reservoir based. The 'data_processing.py' script has an example of using these timeseries files for analysis.
### Contact
Zach Brodeur, zpbrodeur@ucsd.edu
