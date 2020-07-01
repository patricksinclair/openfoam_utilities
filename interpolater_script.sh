#!/bin/bash

#MAKE SURE THAT STARTFROM IN THE CONTROLDICT IS SET TO LATEST TIME

dynamicMeshFilePath='../../d_92_thickBiofilm/quad_riblet/'
#dynamicMeshTime0='../../d_92_thickBiofilm/quad_riblet/
dynamicMeshTime0="$dynamicMeshFilePath/0"


#these next two commands make sure there aren't any time directories in the target case that could
#interfere with the mapFields utility
foamListTimes -rm
#rm 0/alpha.biofilm
setFields

for t in $(seq 0 0.1 30);
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

