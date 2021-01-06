# trace generated using paraview version 5.6.0
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#README:
#This is an improved script for generating the volume data in ParaView.
#It is somewhat simpler than the surface data one as we don't need to extract specific blocks.
#To use it, simply load in the dataset including the grad(U) and dUdt fields.
#You may now use this macro.  It will automatically select Cell Data in the spreadsheet.
#MAKE SURE TIME RANGE AND TIME STEPS ARE CORRECT

delta_t = 0.2
t_max = 20
n_steps = int(t_max/delta_t)
directory_name = 'volume_data'

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1521, 795]

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

# create a new 'Cell Size'
cellSize1 = CellSize(Input=a3D_ribletOpenFOAM)

# Properties modified on cellSize1
cellSize1.ComputeVertexCount = 0
cellSize1.ComputeLength = 0

# show data in view
cellSize1Display = Show(cellSize1, spreadSheetView1)

# hide data in view
Hide(a3D_ribletOpenFOAM, spreadSheetView1)

# update the view to ensure updated data information
spreadSheetView1.Update()

# Properties modified on spreadSheetView1
spreadSheetView1.FieldAssociation = 'Cell Data'

# Properties modified on spreadSheetView1
spreadSheetView1.HiddenColumnLabels = ['Cell Type']


for i in range(n_steps+1):
    t_val = delta_t*i
    # export view
    ExportView(directory_name+'/volume_data-t='+str(t_val)+'.csv', view=spreadSheetView1)
    # get animation scene
    animationScene1 = GetAnimationScene()
    animationScene1.GoToNext()


#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
