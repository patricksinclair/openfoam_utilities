#!/bin/bash

#MAKE SURE THAT STARTFROM IN THE CONTROLDICT IS SET TO LATEST TIME
#ALSO MAKE SURE THAT THAT 0/alpha.biofilm IN THE SOURCE DIRECTORY HAS BEEN DELETED
#ALSO MAKE SURE THAT THE TIME SEQUENCE IS CORRECT.

sed -i '/startFrom/c\startFrom       latestTime;' system/controlDict #makes sure that mapfields maps to the latest time directory


dynamicMeshFilePath='../../d_23_thickBF/3D_riblet'
dynamicMeshTime0="$dynamicMeshFilePath/0"


#these next two commands make sure there aren't any time directories in the target case that could
#interfere with the mapFields utility
foamListTimes -rm
#rm 0/alpha.biofilm
setFields

for t in $(seq 0 0.2 15);
do

  #this removes the .0 from certain values of t, so that t is consisten with OpenFOAM
  if [ "${t: -1}" -eq 0 ];
  then
    t=${t::-2}
  fi

  cp -r $dynamicMeshTime0 $t
  #use sed to change the $t/uniform/time value (optional I think)
  

  mapFields -consistent -sourceTime $t $dynamicMeshFilePath -mapMethod mapNearest
  
done

#make directories to save the volume/surface integral raw data in, as well as one for the processed integral data
mkdir surface_data
mkdir volume_data
mkdir integral_results

