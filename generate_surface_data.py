# trace generated using paraview version 5.6.0
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#README:
#This is a slightly improved script for use in ParaView to generate the surface data.  
#To use it, load in the dataset, including the grad(U) and dUdt fields.  
#Then close the RenderView window and open up a SpreadSheetView window.
#Make sure Cell Data is selected in the spreadsheet.
#Then use the Extract Blocks filter to select the surfaces of interest.
#You may now use this macro.
#MAKE SURE TIME RANGE AND TIME STEPS ARE CORRECT

delta_t = 0.2
t_max = 20
n_steps = int(t_max/delta_t)
directory_name = 'surface_data'

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# find source
extractBlock1 = FindSource('ExtractBlock1')

# create a new 'Cell Size'
cellSize1 = CellSize(Input=extractBlock1)

# Properties modified on cellSize1
cellSize1.ComputeVertexCount = 0
cellSize1.ComputeLength = 0

# get active view
spreadSheetView1 = GetActiveViewOrCreate('SpreadSheetView')
# uncomment following to set a specific view size
# spreadSheetView1.ViewSize = [400, 400]

# show data in view
cellSize1Display = Show(cellSize1, spreadSheetView1)

# hide data in view
Hide(extractBlock1, spreadSheetView1)

# find source
a3D_ribletOpenFOAM = FindSource('3D_riblet.OpenFOAM')

# update the view to ensure updated data information
spreadSheetView1.Update()

# create a new 'Generate Surface Normals'
generateSurfaceNormals1 = GenerateSurfaceNormals(Input=cellSize1)

# Properties modified on generateSurfaceNormals1
generateSurfaceNormals1.FlipNormals = 1
generateSurfaceNormals1.ComputeCellNormals = 1

# show data in view
generateSurfaceNormals1Display = Show(generateSurfaceNormals1, spreadSheetView1)

# hide data in view
Hide(cellSize1, spreadSheetView1)

# update the view to ensure updated data information
spreadSheetView1.Update()

# Properties modified on spreadSheetView1
spreadSheetView1.HiddenColumnLabels = ['Cell Type']


for i in range(n_steps+1):
    t_val = delta_t*i
    # export view
    ExportView(directory_name+'/surface_data-t='+str(t_val)+'.csv', view=spreadSheetView1)
    # get animation scene
    animationScene1 = GetAnimationScene()
    animationScene1.GoToNext()


#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
