#!/bin/bash
#this is a master script that runs all the data pre-processing scripts
#up to the point that ParaView needs to be used to generate the .csv files

#START BY MAKING A COPY OF THE DYNAMIC MESH SOURCE DATA INTO A NEW DIRECTORY
#RUN THIS SCRIPT IN THE NEW COPIED DIRECTORY
#MAKE SURE dUdt_calculator HAS THE RIGHT BOUNDARY NAMES IN IT - THIS WILL DEPEND ON WHAT ANGLE OF FLOW YOU'RE USING
#MAKE SURE THE NAMES ARE CORRECT IN BOTH THE READ AND WRITE METHODS
#WILL NEED TO MODIFY THE dUdt PYTHON FILE FOR THE 45 DEGREE FLOW.
#MAKE SURE THAT THE NEW BLOCKMESHDICT FOR THE INTERPOLATED SYSTEM HAS BEEN CREATED WITH THE CORRECT CELL VALUES
#AND BLOCKMESH HAS BEEN RUN.

#MAKE SURE THAT THE FILEPATH TO THE SOURCE DATA IS CORRECT
#pass the filepath to the dynamic mesh data via the command line
dynamicMeshFilePath=$1
dynamicMeshTime0="$dynamicMeshFilePath/0"
t_final=20
delta_t=0.2

# --- End Definitions Section ---
# check if we are being sourced by another script or shell
#this allows us to take the variables in this script and use them elsewhere
#by sourcing this script, but it doesn't run anything below this next line
[[ "${#BASH_SOURCE[@]}" -gt "1" ]] && { return 0; }
# --- Begin Code Execution Section ---


sed -i '/startFrom/c\startFrom       latestTime;' system/controlDict #makes sure that mapfields maps to the latest time directory
#remove the alpha.biofilm from the source 0 directory
rm $dynamicMeshTime0/alpha.biofilm

#remove the time directories from the target case so that they don't interfere with mapFields
foamListTimes -rm
rm 0/alpha.biofilm
setFields

for t in $(seq 0 $delta_t $t_final);
do
  #this removes the .0 from certain values of t, so that t is consistent with OpenFOAM directory naming convention
  if [ "${t: -1}" -eq 0 ];
  then
    t=${t::-2}
  fi

  cp -r $dynamicMeshTime0 $t
  mapFields -consistent -sourceTime $t $dynamicMeshFilePath -mapMethod mapNearest

done


#make directories to save the volume/surface integral raw data in, as well as one for the processed integral data
mkdir surface_data
mkdir volume_data
mkdir integral_results

#convert from binary to ascii
sed -i '/writeFormat/c\writeFormat     ascii;' system/controlDict
foamFormatConvert

#run the postProcess utility to get the velocity gradient
postProcess -func "grad(U)"
#calculate the time derivatives
python dUdt_calculator.py $t_final $delta_t
#open ParaView to generate the csv files
paraFoam &
