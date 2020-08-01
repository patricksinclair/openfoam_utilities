import numpy as np
import re
import math
match_number = re.compile('-?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *-?\ *[0-9]+)?')



def main():

    t_max = 15
    delta_t = 0.2

    for t in np.arange(0, t_max+delta_t, delta_t):
        print(t)
        write_dUdt(t, delta_t, t_max)



def getU(t):
    '''
    for a given timestep, this method extracts the velocity data from the openfoam file
    returns the velocity data in a numpy array, where each entry is the velocity in a cell

    '''
    t_string = "{:.1f}".format(t)

    #removes trailing 0 and decimal point to be consistent with openfoam
    #directory naming structure
    if t_string[-1] == '0':
        t_string = t_string[:-2]

    filename = t_string+'/U'
    internal_mesh = []
    outlet_boundary = []

    with open(filename) as u_file:

        while True:
            line = u_file.readline()

            #this if statement gets us to the line of interest where all the values are
            if line.startswith('internalField'):
                break
        next(u_file)
        next(u_file)

        #this section gets the values of the internal mesh cells
        while(True):
            line = u_file.readline()
            if "boundaryField" in line:
                break
            else:
                #this is a rather hacky way of dealing with the closing bracket of the internal mesh
                #list of vectors
                if len(line) > 2:
                    #this finds all numbers enclosed in brackets
                    internal_mesh.append(re.search(r'\((.*?)\)',line).group(1))


        #this section gets the values of the rear boundary
        while(True):

            line = u_file.readline()
            if "backWall" in line:
                #skips to the relevant values
                next(u_file)
                next(u_file)
                next(u_file)
                next(u_file)
                next(u_file)
                break


        while(True):
            line = u_file.readline()
            if ";" in line:
                break
            else:
                if len(line) > 2:
                    outlet_boundary.append(re.search(r'\((.*?)\)',line).group(1))

    #iterated backwards here because earlier version needed to delete entries from list
    #can probably just iterate in the usual way now
    for i in range(len(internal_mesh)-1, -1, -1):

        internal_mesh[i] = internal_mesh[i].strip().split(' ')
        internal_mesh[i] = [re.findall(match_number, u)[0] for u in internal_mesh[i] if re.findall(match_number, u)]
        internal_mesh[i] = [float(u) for u in internal_mesh[i] if u]

        if i < len(outlet_boundary):
            outlet_boundary[i] = outlet_boundary[i].strip().split(' ')
            outlet_boundary[i] = [re.findall(match_number, u)[0] for u in outlet_boundary[i] if re.findall(match_number, u)]
            outlet_boundary[i] = [float(u) for u in outlet_boundary[i] if u]



    internal_mesh_array = np.array([np.array(u) for u in internal_mesh])
    outlet_boundary_array = np.array([np.array(u) for u in outlet_boundary])

    return internal_mesh_array, outlet_boundary_array



def calc_dUdt(t, delta_t, t_max):
    '''this method returns an approximation of the time derivatives du/dt for the internal mesh and for the outlet boundary

    it uses the central difference method to calculate the derivatives, and forwards/backwards difference for the
    boundary cases

    returns an array with the differences
    '''

    if math.isclose(t, 0):
        #boundary case, use forward difference method
        t2 = t+delta_t
        t1 = t

        u2_internal, u2_boundary = getU(t2)
        u1_internal = np.zeros_like(u2_internal)
        u1_boundary = np.zeros_like(u2_boundary)

        dUdt_internal = (u2_internal - u1_internal)/delta_t
        dUdt_boundary = (u2_boundary - u1_boundary)/delta_t

    elif math.isclose(t, t_max):
        #boundary case, use backward difference method
        t2 = t
        t1 = t-delta_t

        u2_internal, u2_boundary = getU(t2)
        u1_internal, u1_boundary = getU(t1)

        dUdt_internal = (u2_internal - u1_internal)/delta_t
        dUdt_boundary = (u2_boundary - u1_boundary)/delta_t

    else:
        #for all other cases, use central difference
        t2 = t+delta_t
        t1 = t-delta_t

        u2_internal, u2_boundary = getU(t2)

        #need to handle the boundary case again in case t1 = 0
        if math.isclose(t1, 0):
            u1_internal = np.zeros_like(u2_internal)
            u1_boundary = np.zeros_like(u2_boundary)
        else:
            u1_internal, u1_boundary = getU(t1)

        dUdt_internal = (u2_internal - u1_internal)/(2.*delta_t)
        dUdt_boundary = (u2_boundary - u1_boundary)/(2.*delta_t)

    return dUdt_internal, dUdt_boundary



def write_dUdt(t, delta_t, t_max):
    '''
    this method writes the calculated time derivatives to an OpenFOAM friendly format with the
    hope that this will allow them to be read into paraview.
    '''
    t_string = "{:.1f}".format(t)
    #removes trailing 0 and decimal point to be consistent with openfoam
    #directory naming structure
    if t_string[-1] == '0':
        t_string = t_string[:-2]

    dUdt_internal, dUdt_boundary = calc_dUdt(t, delta_t, t_max)

    filename = t_string+'/dUdt'

    with open(filename, 'w+') as file:

        file.write("/*--------------------------------*- C++ -*----------------------------------*\\\n")
        file.write("  =========                 |\n")
        file.write("  \\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox\n")
        file.write("   \\\    /   O peration     | Website:  https://openfoam.org\n")
        file.write("    \\\  /    A nd           | Version:  7\n")
        file.write("     \\\/     M anipulation  |\n")
        file.write("\\*---------------------------------------------------------------------------*/\n")
        file.write("FoamFile\n")
        file.write("{\n")
        file.write("version     2.0;\n")
        file.write("format      ascii;\n")
        file.write("class       volVectorField;\n")
        file.write('location    "'+t_string+'";\n')
        file.write("object      dUdt;\n")
        file.write("}\n")
        file.write("// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n")

        file.write("\ndimensions      [0 1 -2 0 0 0 0];\n")

        #write the internal mesh values
        file.write("\ninternalField   nonuniform List<vector>\n")
        file.write(str(len(dUdt_internal))+"\n")
        file.write("(\n")

        for i in range(len(dUdt_internal)):
            file.write('({:.5e} {:.5e} {:.5e})\n'.format(dUdt_internal[i][0], dUdt_internal[i][1], dUdt_internal[i][2]))

        file.write(")\n")
        file.write(";\n")

        #boundary values
        file.write("\nboundaryField\n")
        file.write("{\n")

        #left wall
        file.write("\tleftWall\n")
        file.write("\t{\n")
        file.write("\t\ttype \t\t slip;\n")
        file.write("\t}\n")

        #right wall
        file.write("\trightWall\n")
        file.write("\t{\n")
        file.write("\t\ttype \t\t slip;\n")
        file.write("\t}\n")

        #lower wall
        file.write("\tlowerWall\n")
        file.write("\t{\n")
        file.write("\t\ttype \t\t noSlip;\n")
        file.write("\t}\n")

        #upper wall
        file.write("\tupperWall\n")
        file.write("\t{\n")
        file.write("\t\ttype \t\t fixedValue;\n")
        file.write("\t\tvalue \t\t uniform (0 0 0);\n") #TIME DERIVATIVE AT TOP OF SYSTEM IS ZERO DUE TO CONSTANT VELOCITY B.C.
        file.write("\t}\n")

        #front wall
        file.write("\tfrontWall\n")
        file.write("\t{\n")
        file.write("\t\ttype \t\t zeroGradient;\n")
        file.write("\t}\n")

        #back wall
        file.write("\tbackWall\n")
        file.write("\t{\n")
        file.write("\t\ttype \t\t inletOutlet;\n")
        file.write("\t\tinletValue \t uniform (0 0 0);\n")
        file.write("\t\tvalue \t\t nonuniform List<vector>\n")
        file.write(str(len(dUdt_boundary))+"\n")
        file.write("(\n")
        for i in range(len(dUdt_boundary)):
            file.write('({:.5e} {:.5e} {:.5e})\n'.format(dUdt_boundary[i][0], dUdt_boundary[i][1], dUdt_boundary[i][2]))
        file.write(")\n")
        file.write(";\n")
        file.write("\t}\n")

        file.write("}\n\n")
        file.write("// ************************************************************************* //")



main()
