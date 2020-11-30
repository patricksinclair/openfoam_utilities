# trace generated using paraview version 5.6.0
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#README:
#This script is used to calculate the volume of biofilm in the system over time.
#At each timestep it uses the "Integrate Variables" filter to calculate the total value of alpha in the system.
#Saves the integral results in a .csv file for each timestep for later processing.
#This macro can be run as soon as the data is loaded and the "skip zero time" box is selected.

#MAKE SURE DELTAT AND MAXT ARE CORRECT, AND SKIP ZERO TIME IS TRUE.
#
delta_t = 0.2
t_max = 20
n_steps = int(t_max/delta_t)
directory_name = 'alpha_data'

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1489, 795]

# destroy renderView1
Delete(renderView1)
del renderView1

# Create a new 'SpreadSheet View'
spreadSheetView1 = CreateView('SpreadSheetView')
spreadSheetView1.ColumnToSort = ''
spreadSheetView1.BlockSize = 1024L
# uncomment following to set a specific view size
# spreadSheetView1.ViewSize = [400, 400]

# get layout
layout1 = GetLayout()

# place view in the layout
layout1.AssignView(0, spreadSheetView1)

# get active source.
a3D_ribletOpenFOAM = GetActiveSource()

# show data in view
a3D_ribletOpenFOAMDisplay = Show(a3D_ribletOpenFOAM, spreadSheetView1)

# Properties modified on spreadSheetView1
spreadSheetView1.FieldAssociation = 'Cell Data'

# create a new 'Integrate Variables'
integrateVariables1 = IntegrateVariables(Input=a3D_ribletOpenFOAM)

# show data in view
integrateVariables1Display = Show(integrateVariables1, spreadSheetView1)

# update the view to ensure updated data information
spreadSheetView1.Update()

#range starts at 1 as we skip 0 time here
for i in range(1, n_steps+1):
    t_val = delta_t*i
    # export view
    ExportView(directory_name+'/alpha_data-t='+str(t_val)+'.csv', view=spreadSheetView1)
    # get animation scene
    animationScene1 = GetAnimationScene()
    animationScene1.GoToNext()

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).