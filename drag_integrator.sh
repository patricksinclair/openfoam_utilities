#!/bin/bash
#script to run the drag integrator python script using the variables in master_script
#i.e. the final time and delta_t.
. ./master_script.sh

python drag_integration_calculator.py $t_final $delta_t
