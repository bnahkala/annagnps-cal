# Brady Nahkala
# Date modified: 2019 AUG 13
# Purpose: Iteratively run AnnAGNPS models of prairie potholes 
# to calibrate for SCS CN and infiltration (retention) values. 
# This cycles through CN and infiltration values, outputting 
# statistical params while utlizing the package 'hydroeval.'
# 
# Date Cleaned: 2020 NOV 10
# Adding comments to clarify code. 

# LIBRARY=================================================

import os
import platform
import sys
import subprocess
from datetime import time
from datetime import date
from datetime import datetime
import numpy
import scipy
from scipy import stats
from statistics import stdev
import hydroeval
from hydroeval import nse
from hydroeval import pbias
from hydroeval import evaluator
from hydroeval import rmse

# SETUP=======================================================

# REFERENCE INFILTRATION VALUE (mm/day)
inf_ref = 0 # the value to center or start your infiltration calibration

# REFERENCE CN VALUES (From NRCS lookup table for specified type)
char = "Straight Row Crop Poor Hydrologic Condition\n"
A_ref = 72 
B_ref = 81
C_ref = 88
D_ref = 91

cn_d = 0 # set range of SCS CN down
cn_u = 0 # set range of SCS CN up
A_min = A_ref - cn_d
A_max = A_ref + cn_u
B_min = B_ref - cn_d
B_max = B_ref + cn_u
C_min = C_ref - cn_d
C_max = C_ref + cn_u
D_min = D_ref - cn_d
D_max = D_ref + cn_u

# FILE NAMES

# wetland data csv input file for annagnps
wetlandin_filename = "C:/AGNPS_Watershed_Studies/Bunny_Pothole_Model_Volume/4_Editor_DataSets/CSV_Input_Files/watershed/AnnAGNPS_Wetland_Data_Section.csv"

# output wetland data file name (annagnps default)
wetSIM_filename = 'C:/AGNPS_Watershed_Studies/Bunny_Pothole_Model_Volume/5_AnnAGNPS_DataSets/AnnAGNPS_SIM_Wetland_Effects.csv'

# runoff curve number input file for annagnps, default name
RCN_filename = "C:/AGNPS_Watershed_Studies/Bunny_Pothole_Model_Volume/4_Editor_DataSets/CSV_Input_Files/general/Runoff_Curve_Number_Data_Input_Editor_v5.5_Format.csv"

# user generated output summary file for each batch of model runs
statssum_filename = "C:/AGNPS_Watershed_Studies/Bunny_Pothole_Model_Volume/9_BAN_calibration/Python_Output/Stats_Summary.csv"

# text file for monitoring data, data with which to calibrate model
obsdata_filename = "C:/AGNPS_Watershed_Studies/Bunny_Pothole_Model_Volume/9_BAN_calibration/Python_Output/Bobs_16_18_volume.txt"

# destination file for copying annagnps output, to calculate calibration statistics
simdata_filename = "C:/AGNPS_Watershed_Studies/Bunny_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_volume.txt"

# YEAR AND POTHOLE
pothole_name = "Bunny\n"    #note: this is a dumb way to do this: take out \n and make a loop when  you write to files - see the alt. mngmt python file
pothole_ID = "B"        
wet_area = 2.35 #hectares
wet_area_m2 = wet_area * 10000 # square meters
max_depth = 1000 #mm

cal_year = "2017-2018\n\n" # for statssum file

# START AND END DATES IN GREGORIAN DAYS (Wetland sim file output)
# write the gregorian days with which you have and would like to extract output data for calibration
start16 = 736104 # 05/20/2016 
end16 = 736246 # 10/9/2016

start17 = 736458 # 05/09/2017
end17 = 736593 # 09/21/2017

start18 = 736838 # 05/24/2018
end18 = 736985 # 10/18/2018

# METADATA/CONSTANTS SETUP =================================================
# INITIATE COUNTER
i = 0 # counts number of model runs

# WETLAND/CN CSV INPUT FILE (prepare file)
headerw = "Wetland_ID,Reach_ID,Wetland_Area,Initial_Water_Depth,Min_Water_Depth,Max_Water_Depth,Water_Temperature,Potential_Daily_Infiltration,Weir_Coef,Weir_Width,Weir_Height,Soluble_N_Conc,Nitrate-N_Loss_Rate,Nitrate-N_Loss_Rate_Coef,Temperature_Coef,Weir_Exp,Input_Units_Code\n"
headerCN = "Curve_Number_ID, CN_A, CN_B, CN_C, CN_D\n" # what I should do is just delete these two and append the two that I want so the whole database is there - see annagnps-alts repository
fallow = "Fallow_(Bare),77.,86.,91.,94.\n"

# STATS OUTPUT FILE METADATA
header = "Execution Date and Start Time:\n"
meta = str(datetime.now()) + "\n"
header2 = "Trial Number, CN_A, CN_B, CN_C, CN_D, Infiltration, NSE, PBIAS, RSR, R2\n"
header3 = "Assumed Field Conditions:\n"
units = "#,-, -, -, -, mm/day\n"
s = open(statssum_filename, "w+")
s.write(header)
s.write(meta)
s.write("Pothole: " + pothole_name)
s.write("Calibration Time Period: " + cal_year)  
s.write(header3)
s.write(char) 
s.write(header2)
s.write(units)
s.close()

# LOOP MAIN PROGRAM =============================================
# THIS RUNS LOOP WITHIN LOOP - AT EACH CN STEP IT LOOPS MULTIPLE INF VALUES
for y in range (0, 1): # change these values for number of times to increment SCS curve number
    inf_min = inf_ref - 0 # change these to establish search space for infiltration
    inf_max = inf_ref + 200
    for x in range (0, 25): # change these for number of times to increment infiltration
        # OPEN AND EDIT WETLAND INPUT CSV
        w = open(wetlandin_filename, "w")
        w.write(headerw)
        wetland_dat = "1,2," + str(wet_area) + ",0.,0.," + str(max_depth) + ",," + str(inf_min) + ".,2.,10.,1.,,,,,1.5,1"
        w.write(wetland_dat)
        w.close()

        # OPEN AND EDIT SCS CN INPUT CSV
        w = open(RCN_filename, "w").close()
        w = open(RCN_filename, "w")
        w.write(headerCN)
        w.write(fallow)
        row_crop = "Row_Crop_(SR_Poor)," + str(A_min) + ".," + str(B_min) + ".," + str(C_min) + ".," + str(D_min) + "."
        w.write(row_crop)
        w.close()

        # EXECUTE 0_DELETE ALL OUTPUT FILES_BAN.BAT FILE
        # this edited .BAT file allows you to skip the AnnAGNPS executable prompt 'do you want to overwrite'
        
        # see alternative management scenario script to see a better way to do this
        subprocess.call([r'C:\AGNPS_Watershed_Studies\Bunny_Pothole_Model_Volume\0_Batch_files\0_delete_all_output_files_BAN.bat'])

        # EXECUTE ANNAGNPS .BAT FILE
        subprocess.call([r'C:\AGNPS_Watershed_Studies\Bunny_Pothole_Model_Volume\0_Batch_files\3_execute_AnnAGNPS_BAN.bat'])
    
        # EXTRACT WETLAND SIM DATA
        wetread = numpy.genfromtxt(fname = wetSIM_filename, delimiter=',', usecols=numpy.arange(0,32), invalid_raise=False)
        
        # VOLUME MODIFICATION: Convert to meters and multiply by wetland area to achieve m^3.
        # COLLECT 2016 SIM DATA
        sim_list = []
        #for k in range(len(wetread)):
            #if (wetread[k, 0] >= start16 and wetread[k, 0] <= end16):
                #sim_list.append(wetread[k, 14] / 1000 * wet_area_m2)
                #k = k + 1

        # APPEND 2017 SIM DATA
        for j in range(len(wetread)):
            if (wetread[j, 0] >= start17 and wetread[j, 0] <= end17):
                sim_list.append(wetread[j, 14] / 1000 * wet_area_m2)
                j = j + 1

        # APPEND 2018 SIM DATA
        for m in range(len(wetread)):
            if (wetread[m, 0] >= start18 and wetread[m, 0] <= end18):
                sim_list.append(wetread[m, 14] / 1000 * wet_area_m2)
                m = m + 1

        b = open("C:/AGNPS_Watershed_Studies/Bunny_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_volume.txt", "w+").close()
        b = open("C:/AGNPS_Watershed_Studies/Bunny_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_volume.txt", "w+")
        for z in range(len(sim_list)):
            b.write(str(sim_list[z])+"\n")
        b.close()

        # CALCULATE EFFICIENCY STATISTICS
        # import and check
        Bobs_16_18_volume = numpy.loadtxt(fname = obsdata_filename) # object is named: B for bunny, obs for 'observed' and then years of data, and metric
        sim_output = numpy.loadtxt(fname = simdata_filename)

        #if not numpy.array_equal(Bobs_16_18_volume, sim_output):
            #raise Exception('The observed and simulated periods (time series length) do not match. ' + str(len(Bobs_16_18_volume)) + "," + str(len(sim_output)))

        # calculate
        b_nse = evaluator(nse, sim_output, Bobs_16_18_volume) # b for bunny, and nse for Nash Sutcliffe efficiency
        b_pbias = evaluator(pbias, sim_output, Bobs_16_18_volume) # percent bias
        b_rmse = evaluator(rmse, sim_output, Bobs_16_18_volume)  # rmse
        sd = stdev(Bobs_16_18_volume) # standard deviation
        b_rsr = b_rmse / sd  # RSR
        b_linr = stats.linregress(Bobs_16_18_volume, sim_output)
        b_r2 = b_linr[2]**2 # R^2

        # WRITE STATISTICS TO SUMMARY FILE
        trialdata = str(i) + "," + str(A_min) + ".," + str(B_min) + ".," + str(C_min) + ".," + str(D_min) + ".," + str(inf_min) + "," + str(b_nse) + "," + str(b_pbias) + "," + str(b_rsr) + "," + str(b_r2) + "\n"
        s = open(statssum_filename, "a")
        s.write(trialdata)
        s.close()

        # increment
        i = i + 1 # next model run
        inf_min = inf_min + 10 # choose infiltration increment
        #if inf_min > inf_max:
            #raise Exception('The program will run past the maximum infiltration value.')
    
    B_min = B_min + 1 # increment CN
    C_min = C_min + 1
    A_min = A_min + 1
    D_min = D_min + 1
    if D_min > 99: 
        D_min = 99

   

