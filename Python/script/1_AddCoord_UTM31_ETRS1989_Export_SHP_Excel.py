# Import arcpy module
import arcpy
import numpy
import os

# Set the input feature class
in_fc = r"\\WM20ocqu46ph01\WF_Projects\NL_IJV\2_FINAL\WINDFARM\WINDFARM.gdb\NL_IJV_RVO_Windfarm_Sites_UTM31N_v1_point"


# Delete the fields and Set the field names to delete
del_fields = ["X_ETRS_UTM31", "Y_ETRS_UTM31","X_ETRS", "Y_ETRS"]
arcpy.DeleteField_management(in_fc, del_fields)


# Set the output coordinate system
out_sr = arcpy.SpatialReference(25831) # ETRS 1989 UTM Zone 31N - 25831

# Add geometry attributes
geom_props = "POINT_X_Y_Z_M"
arcpy.AddGeometryAttributes_management(in_fc, geom_props , "", "", out_sr)


# Rename the fields POINT_X and POINT_Y to X_COORD and Y_COORD
arcpy.AlterField_management(in_fc, "POINT_X", "X_ETRS_UTM31", "Easting [ETRS 1989 UTM31] ")
arcpy.AlterField_management(in_fc, "POINT_Y", "Y_ETRS_UTM31", "Northing [ETRS 1989 UTM31]")

# Create an update cursor to access the rows of the feature class
with arcpy.da.UpdateCursor(in_fc, ["X_ETRS_UTM31", "Y_ETRS_UTM31"]) as cursor:
    # Loop through each row
    for row in cursor:
        # Round the coordinates to 1 decimal place using numpy.round
        row[0] = numpy.round(row[0], 0)
        row[1] = numpy.round(row[1], 0)
        # Update the row with the rounded values
        cursor.updateRow(row)

# Set the output coordinate system
out_sr = arcpy.SpatialReference(4258) # ETRS1989 - 4258
geom_props = "POINT_X_Y_Z_M"
arcpy.AddGeometryAttributes_management(in_fc, geom_props , "", "", out_sr)
# Rename the fields POINT_X and POINT_Y to X_COORD and Y_COORD
arcpy.AlterField_management(in_fc, "POINT_X", "X_ETRS", "X [ETRS 1989]")
arcpy.AlterField_management(in_fc, "POINT_Y", "Y_ETRS", "Y [ETRS 1989]")


directory_excel = r"\\WM20ocqu46ph01\WF_Projects\NL_IJV\4_OUTPUT\_WindFarm"

# Extract directory and file name
file_path = os.path.dirname(in_fc)
file_name = in_fc.split(os.path.sep)[-1]
excel_name = file_name +".xlsx"
shp_name = file_name +".shp"


ouput_excel = os.path.join(directory_excel, excel_name)
output_shapefile = os.path.join(directory_excel, shp_name)

print("Full Path:", in_fc)
print("Directory:", file_path)
print("Excel Path:", ouput_excel)
print("Shp Path:", output_shapefile)


# Export attribute table to Excel
arcpy.TableToExcel_conversion(in_fc, ouput_excel)

# Export feature class to shapefile
arcpy.CopyFeatures_management(in_fc, output_shapefile)

print("Attribute table:", output_shapefile)
print("Shapefile:", ouput_excel )









