TITLE DELETE ALL NON-ORIGINAL FILES
ECHO off

CD ..\5_AnnAGNPS_DataSets
DEL AnnAGNPS*.*
DEL Dayclim*.*
DEL CSV_Export.rpt
DEL Source_Load_Contributing_Area_Graph.xlsx
RD climate /S /Q
RD general /S /Q
RD simulation /S /Q
RD watershed /S /Q
RD CSV_Files /S /Q
RD CSV_Output_Files /S /Q
REM 5_AnnAGNPS_Datasets deletions done!

CD ..\6_Output_DataSets
DEL *.csv
DEL *.err
DEL *.log
DEL *.TXT
Rem 6_Output_Datasets deletions done!

ECHO ************************************************
ECHO **** Execution of file deletions completed! ****
ECHO ************************************************
