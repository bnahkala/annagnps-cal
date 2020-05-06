# Brady Nahkala
# Date modified: 2019 AUG 16
# Purpose: Iteratively run AnnAGNPS models of prairie potholes 
# to calibrate for SCS CN and infiltration (retention) values. 
# This cycles through CN and infiltration values, outputting 
# statistical params while utlizing the package 'hydroeval.'
# 
# This version inefficiently processes multiple potholes in a
# singular model. This could be rewritten to strip the existing
# wetland data file and automatically run how many wetlands 
# were needed. 
# 
# =============================================================

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
inf_ref = 70

# INPUT FIELD CHARACTERISTIC
char = "Straight Row Crop Poor Hydrologic Condition\n"
# INPUT CN FOR B SOILS
B_ref = 81
# INPUT CN FOR C SOILS
C_ref = 88
# INPUT A AND D - NEEDED FOR ANNAGNPS TO RUN WELL
A_ref = 72
D_ref = 91

cn_d = 2
cn_u = 2
A_min = A_ref - cn_d
A_max = A_ref + cn_u
B_min = B_ref - cn_d
B_max = B_ref + cn_u
C_min = C_ref - cn_d
C_max = C_ref + cn_u
D_min = D_ref - cn_d
D_max = D_ref + cn_u

# FILE NAMES
wetlandin_filename = "C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/4_Editor_DataSets/CSV_Input_Files/watershed/AnnAGNPS_Wetland_Data_Section.csv"
wetSIM_filename = 'C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/5_AnnAGNPS_DataSets/AnnAGNPS_SIM_Wetland_Effects.csv'
RCN_filename = "C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/4_Editor_DataSets/CSV_Input_Files/general/Runoff_Curve_Number_Data_Input_Editor_v5.5_Format.csv"
statssum_filename = "C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/Stats_Summary.csv"
obsdata_filename_1 = "C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/Hobs_18_volume.txt"
simdata_filename_1 = "C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_H.txt"
obsdata_filename_2 = "C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/Pobs_18_volume.txt"
simdata_filename_2 = "C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_P.txt"

# YEAR AND POTHOLE
pothole_name = "HenPlume\n"
pothole_ID = "HP"        # Walnut = W; Cardinal = C; Lettuce = L; Gravy = G; Hen = H; Plume = P; Mouth = M
cal_year = "2018\n\n"

# pothole 1 - hen
wetlandID_1 = 1
reachID_1 = 9
wet_area_1 = 0.35    # gisdV
wet_area_1_m2 = wet_area_1 * 10000
max_depth_1 = 520
weir_height_1 = max_depth_1 / 1000

# POTHOLE 2 - plume
wetlandID_2 = 2
reachID_2 = 2
wet_area_2 = 0.45   # GIS maximum
wet_area_2_m2 = wet_area_2 * 10000
max_depth_2 = 450
weir_height_2 = max_depth_2 / 1000

# START AND END DATES IN GREGORIAN DAYS (Wetland sim file output)
# dates currently confirmed for HenPlume only
##start16 = 736111 # 05/27/2016 
#end16 = 736246 # 10/9/2016

#start17 = 736458 # 05/09/2017 # confirmed
#end17 = 736626 # 10/24/2017

start18 = 736838 # 05/24/2018 # confirmed
end18 = 736988 # 10/21/2018

# METADATA/CONSTANTS SETUP =================================================
# INITIATE COUNTER
i = 0

# WETLAND/CN CSV INPUT FILE
headerw = "Wetland_ID,Reach_ID,Wetland_Area,Initial_Water_Depth,Min_Water_Depth,Max_Water_Depth,Water_Temperature,Potential_Daily_Infiltration,Weir_Coef,Weir_Width,Weir_Height,Soluble_N_Conc,Nitrate-N_Loss_Rate,Nitrate-N_Loss_Rate_Coef,Temperature_Coef,Weir_Exp,Input_Units_Code\n"
headerCN = "Curve_Number_ID, CN_A, CN_B, CN_C, CN_D\n" # what I should do is just delete these two and append the two that I want so the whole database is there
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
for y in range (0,5):
    inf_min = inf_ref - 8
    inf_max = inf_ref + 10
    for x in range (0, 10):
        # OPEN AND EDIT WETLAND INPUT CSV
        w = open(wetlandin_filename, "w")
        w.write(headerw)
        wetland_dat_1 = str(wetlandID_1) + "," + str(reachID_1) + "," + str(wet_area_1) + ",0.,0.," + str(max_depth_1) + ",," + str(inf_min) + ".,2.,10.," + str(weir_height_1) + ",,,,,1.5,1\n"
        wetland_dat_2 = str(wetlandID_2) + "," + str(reachID_2) + "," + str(wet_area_2) + ",0.,0.," + str(max_depth_2) + ",," + str(inf_min) + ".,2.,10.," + str(weir_height_2) + ",,,,,1.5,1\n"
        w.write(wetland_dat_1)
        w.write(wetland_dat_2)
        w.close()

        # OPEN AND EDIT SCS CN INPUT CSV
        w = open(RCN_filename, "w").close()
        w = open(RCN_filename, "w")
        w.write(headerCN)
        w.write(fallow)
        row_crop = "Row_Crop_(SR_Poor)," + str(A_ref) + ".," + str(B_min) + ".," + str(C_min) + ".," + str(D_ref) + "."
        w.write(row_crop)
        w.close()

        # EXECUTE 0_DELETE ALL OUTPUT FILES_BAN.BAT FILE
        # this allows you to skip the AnnAGNPS executable prompt 'do you want to overwrite'
        subprocess.call([r'C:\AGNPS_Watershed_Studies\HenPlume_Pothole_Model_Volume\0_Batch_files\0_delete_all_output_files_BAN.bat'])

        # EXECUTE ANNAGNPS .BAT FILE
        subprocess.call([r'C:\AGNPS_Watershed_Studies\HenPlume_Pothole_Model_Volume\0_Batch_files\3_execute_AnnAGNPS_BAN.bat'])
    
        # EXTRACT WETLAND SIM DATA
        wetread = numpy.genfromtxt(fname = wetSIM_filename, delimiter=',', usecols=numpy.arange(0,32), invalid_raise=False)

        # COLLECT 2016 SIM DATA
        sim_list_1 = []
        sim_list_2 = []
        #for k in range(len(wetread)):
            #if (wetread[k, 0] >= start16 and wetread[k, 0] <= end16):
                #sim_list.append(wetread[k, 14] / 1000)
                #k = k + 1

        # APPEND 2017 SIM DATA
        #for j in range(len(wetread)):
            #if (wetread[j, 0] >= start17 and wetread[j, 0] <= end17):
                #sim_list.append(wetread[j, 14] / 1000)
                #j = j + 1

        # APPEND 2018 SIM DATA
        for m in range(len(wetread)):
            if (wetread[m, 0] >= start18 and wetread[m, 0] <= end18 and wetread[m, 4] == wetlandID_1):
                sim_list_1.append(wetread[m, 14] / 1000 * wet_area_1_m2)
                m = m + 1

        for q in range(len(wetread)):
            if (wetread[q, 0] >= start18 and wetread[q, 0] <= end18 and wetread[q, 4] == wetlandID_2):
                sim_list_2.append(wetread[q, 14] / 1000 * wet_area_2_m2)
                q = q + 1

        b = open("C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_H.txt", "w+").close()
        b = open("C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_H.txt", "w+")
        for z in range(len(sim_list_1)):
            b.write(str(sim_list_1[z])+"\n")
        b.close()

        c = open("C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_P.txt", "w+").close()
        c = open("C:/AGNPS_Watershed_Studies/HenPlume_Pothole_Model_Volume/9_BAN_calibration/Python_Output/sim_output_P.txt", "w+")
        for d in range(len(sim_list_2)):
            c.write(str(sim_list_2[d])+"\n")
        c.close()

        # CALCULATE EFFICIENCY STATISTICS
        # import and check
        Hobs_18_volume = numpy.loadtxt(fname = obsdata_filename_1)
        sim_output_H = numpy.loadtxt(fname = simdata_filename_1)
        Pobs_18_volume = numpy.loadtxt(fname = obsdata_filename_2)
        sim_output_P = numpy.loadtxt(fname = simdata_filename_2)

        #if not numpy.array_equal(Hobs_18_volume, sim_output_H):
            #raise Exception('The observed and simulated periods (time series length) do not match. ' + str(len(Hobs_18_volume)) + "," + str(len(sim_output_H)))

        # calculate - hen
        H_nse = evaluator(nse, sim_output_H, Hobs_18_volume) 
        H_pbias = evaluator(pbias, sim_output_H, Hobs_18_volume) 
        H_rmse = evaluator(rmse, sim_output_H, Hobs_18_volume) 
        sd_1= stdev(Hobs_18_volume)
        H_rsr = H_rmse / sd_1 
        H_linr = stats.linregress(Hobs_18_volume, sim_output_H)
        H_r2 = H_linr[2]**2

        # calculate - plume
        P_nse = evaluator(nse, sim_output_P, Pobs_18_volume) 
        P_pbias = evaluator(pbias, sim_output_P, Pobs_18_volume) 
        P_rmse = evaluator(rmse, sim_output_P, Pobs_18_volume) 
        sd_2 = stdev(Pobs_18_volume)
        P_rsr = P_rmse / sd_2 
        P_linr = stats.linregress(Pobs_18_volume, sim_output_P)
        P_r2 = P_linr[2]**2

        # WRITE TO SUMMARY FILE
        trialdata_1 = str(i) + "," + str(A_min) + ".," + str(B_min) + ".," + str(C_min) + ".," + str(D_min) + ".," + str(inf_min) + "," + str(H_nse) + "," + str(H_pbias) + "," + str(H_rsr) + "," + str(H_r2) + ",Hen\n"
        trialdata_2 = str(i) + "," + str(A_min) + ".," + str(B_min) + ".," + str(C_min) + ".," + str(D_min) + ".," + str(inf_min) + "," + str(P_nse) + "," + str(P_pbias) + "," + str(P_rsr) + "," + str(P_r2) + ",Plume\n"
        s = open(statssum_filename, "a")
        s.write(trialdata_1)
        s.write(trialdata_2)
        s.close()

        # increment
        i = i + 1 
        inf_min = inf_min + 2
        #if inf_min > inf_max:
            #raise Exception('The program will run past the maximum infiltration value.')
    
    B_min = B_min + 1
    C_min = C_min + 1
    A_min = A_min + 1
    D_min = D_min + 1
    if D_min > 99: 
        D_min = 99

   

