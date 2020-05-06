TITLE ANNAGNPS EXECUTION
ECHO off
ECHO ***
ECHO *** This batch file assumes this is run from the location in the
ECHO *** directory structure in the form of the following example:
ECHO ***
ECHO *** C:\AGNPS_Watershed_Studies\OH_AGNPS_Example_Watershed\0_Batch_files
ECHO ***

CD ..\5_AnnAGNPS_DataSets

ECHO Cleanup old files
DEL AnnAGNPS*.*

ECHO Copy watershed and climate input files
COPY ..\4_Editor_Datasets\CSV_Input_Files\AnnAGNPS.fil
COPY ..\4_Editor_Datasets\CSV_Input_Files\annagnps_master.csv
XCOPY ..\4_Editor_Datasets\CSV_Input_Files\climate climate /e /q /i
XCOPY ..\4_Editor_Datasets\CSV_Input_Files\general general /e /q /i
XCOPY ..\4_Editor_Datasets\CSV_Input_Files\Output Output /e /q /i
XCOPY ..\4_Editor_Datasets\CSV_Input_Files\simulation simulation /e /q /i
XCOPY ..\4_Editor_Datasets\CSV_Input_Files\watershed watershed /e /q /i

ECHO Execute AnnAGNPS
CALL ..\..\..\Agnps\PLMODEL\EXECUTE\AnnAGNPS.exe

ECHO
ECHO ******************************************
ECHO **** Execution of AnnAGNPS completed! ****
ECHO ******************************************

