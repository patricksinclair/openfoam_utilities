#!/bin/bash
#this script copies all the necessary files to the target directory
#run it on the command line with the target file directory as a command line argument
target_dir=$1

cp master_script.sh drag_integrator.sh dUdt_calculator.py drag_integration_calculator.py $target_dir
