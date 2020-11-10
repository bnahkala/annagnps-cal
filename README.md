# AnnAGNPS Calibration Scripts
Step-wise calibration of AnnAGNPS using Python. These scripts assume:
1. You have built the AnnAGNPS model, including DEM processing with TOPAGNPS, soil, field and management attributes have been added, etc.
2. The prairie pothole as been placed in the watershed using the 'wetland data' field. 
3. You are attempting to calibrate only curve number and infiltration. 

Calibration is performed by calculating NSE, PBIAS, R2, and RSR for water volume in the wetland module, to emulate prairie potholes in the Des Moines Lobe of Iowa. 

Methods used in upcoming technical memo, to be submitted to Applied Engineering in Agriculture. Methods and models further used to calibrate baseline models and alternative management scenarios for thesis and publication work. 

Nahkala, B. A. (2020). Watershed modeling and random forest flood risk classification of farmed prairie potholes. Master's Thesis. ISU Digital Repository. 19114. 
