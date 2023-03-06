# Import arcpy module
import arcpy
import datetime
import os
import arcpy.cartography as CA

#----------------------------------------------------------------------
# 1. Get parameters from the toolbox using 'GetParametersAsText' method
#----------------------------------------------------------------------

Land = arcpy.GetParameterAsText(0)
Intertidal = arcpy.GetParameterAsText(1)
Reef = arcpy.GetParameterAsText(2)
NoFeasible = arcpy.GetParameterAsText(3)
tolerance = arcpy.GetParameterAsText(4)
if tolerance == '#' or not tolerance:
   tolerance = 50
   
      
#----------------------------------------------------------------------   
# 0. Function
#----------------------------------------------------------------------
def create_folder(directory, name):
    directory_new = os.path.join(directory, name) 
    if not os.path.exists(directory_new):
        os.makedirs(directory_new)
    return directory_new 
    
def find_grep(d, s): # Wrap this up as a nice function with a docstring.
    "Returns list of files in directory d which have the string s"
    files = os.listdir(d) # Use better names than "List"
    matched_files = []    # List to hold matched file names
    for f in files:       # Loop over files
        full_name = os.path.join(d, f) # Get full name to the file in question
        if os.path.isfile(full_name): # We need to only look through files (skip directories)
            with open(full_name) as fp:
                if full_name.endswith('.shp'):# Open the file
                    if s in full_name:
                        matched_files.append(full_name)                   
    return matched_files # Return a list of matched files  

def FieldInsertDir (d, field, datatype, value):
    files = os.listdir(d)
    for file in files:
        if file.endswith('.shp'):
            arcpy.AddField_management(os.path.join(d,file), field, datatype) 
            arcpy.CalculateField_management((os.path.join(d,file)), field, value,"PYTHON_9.3")
            
def FieldInsertFile (file, field, datatype, value):
    arcpy.AddField_management(file, field, datatype) 
    arcpy.CalculateField_management(file, field, value,"PYTHON_9.3")
            
def FieldClass (d, field, datatype, value):
    files = os.listdir(d)
    for file in files:
        if file.endswith('.shp'):
            arcpy.AddField_management(os.path.join(d,file), field, datatype) 
            arcpy.CalculateField_management((os.path.join(d,file)), field, value,"PYTHON_9.3")
            
def DeleteField(d, DontDeleteFields):
    files = os.listdir(d)
    for file in files:
        if file.endswith('.shp'):
            for f in arcpy.ListFields(os.path.join(d,file)):
                arcpy.AddMessage(f) 
                if f.name not in set(DontDeleteFields):
                    arcpy.DeleteField_management(os.path.join(d,file),f.name)
DontDeleteField = ['FID', 'Shape', 'Class', 'Version', 'Date']


def PolygonToLine(dir1, dir2):
    files = os.listdir(dir1)
    for file in files:
        if file.endswith('.shp'):
            if not os.path.exists(os.path.join(dir2,file)):
                arcpy.PolygonToLine_management(os.path.join(dir1,file), os.path.join(dir2,file)) 

#----------------------------------------------------------------------   
# 1. Create a list of input files
#----------------------------------------------------------------------

arcpy.AddMessage("1. Check input files: ")

files = [Land,Intertidal,Reef,NoFeasible]
file_name = ['Land','Intertidal','Reef','NoFeasible']
shapefiles = []
i = 0

for file in files: 
    if arcpy.Exists(file):
        path, filename = os.path.split(file)
        arcpy.AddMessage(" " + str(i) + ") " + filename + " File exist")
        shapefiles.append(file)
    else:
        arcpy.AddMessage(" " + str(i) + ") " + str(file_name[i]) + " file NOT exist")
        #arcpy.AddMessage( file_name[str(i)])
    i = 1 + i
        
arcpy.AddMessage(" DONE")
           
#----------------------------------------------------------------------
# 2. Create folders
#----------------------------------------------------------------------
arcpy.AddMessage("2. Creating Folders")

dir_Temp = create_folder(path, 'Temp')

dir_dissolve = create_folder(dir_Temp, 'Dissolve')         
dir_temp_smooth_line = create_folder(dir_Temp, 'Smooth_Line')    
dir_temp_smooth_pol = create_folder(dir_Temp, 'Smooth_Polygon') 

dir_temp_pixel_line = create_folder(dir_Temp, 'Pixel_Line') 
dir_temp_pixel_pol = create_folder(dir_Temp, 'Pixel_Polygon') 

dir_delivery = create_folder(path, 'Deliverables') 
dir_delivery_pixel = create_folder(dir_delivery,'Pixel') 
dir_delivery_smooth = create_folder(dir_delivery,'Smooth') 

arcpy.AddMessage(" DONE")

#----------------------------------------------------------------------   
# X. Delete clear files/folder
#----------------------------------------------------------------------   

folder = dir_dissolve

for the_file in os.listdir(folder):
    if ".lock" in the_file:
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                arcpy.AddMessage("if lock DONE")
            else:
                shutil.rmtree(file_path)
                arcpy.AddMessage(" lock DONE")
        except Exception, e:
            arcpy.AddMessage(e)

#----------------------------------------------------------------------
# 3. Calculate new Class Field as a new SHP
#----------------------------------------------------------------------
arcpy.AddMessage("3. Shapefiles with ID Field")
                
# Create new version of shp with Field "Class"
for file in shapefiles:
    path, filename = os.path.split(file)
    directory_new = os.path.join(dir_dissolve,filename) 
    if not os.path.exists(directory_new):
        file_ID = arcpy.management.CopyFeatures(file, os.path.join(dir_dissolve,filename)) 
        arcpy.AddField_management(file_ID,'Class', 'TEXT')  
        if file.endswith('Land.shp'):
            arcpy.CalculateField_management(file_ID, "Class","'Land'", "PYTHON_9.3")
        if file.endswith('Intertidal.shp'):
            arcpy.CalculateField_management(file_ID, "Class","'Intertidal'", "PYTHON_9.3")
        if file.endswith('Reef.shp'):
            arcpy.CalculateField_management(file_ID, "Class","'Reef'", "PYTHON_9.3")
        if file.endswith('feasible.shp'):
            arcpy.CalculateField_management(file_ID, "Class","'NotFeasible'", "PYTHON_9.3")  

arcpy.AddMessage(" DONE")

#----------------------------------------------------------------------
# 4. Merge Polygon Shapefiles 
#----------------------------------------------------------------------
arcpy.AddMessage("4. Merge Polygon Shapefiles")

if not os.path.exists(os.path.join(dir_dissolve,'Merge.shp')):
    arcpy.AddMessage(" Merging Shapefiles...")
    shp_merge = find_grep(dir_dissolve,'.shp')
    Merge = arcpy.Merge_management(shp_merge, os.path.join(dir_dissolve,'Merge'))

arcpy.AddMessage(" DONE")

#----------------------------------------------------------------------
# 5. Dissolve Shapefiles 
#----------------------------------------------------------------------
arcpy.AddMessage("5. Dissolve Polygons")

if not os.path.exists(os.path.join(dir_dissolve,'Dissolve.shp')):
    arcpy.AddMessage(" Dissolving Polygons...")
    Dissolve_polygons = arcpy.Dissolve_management(os.path.join(dir_dissolve,'Merge.shp'), os.path.join(dir_dissolve,'Dissolve'),
                            "Class", "","SINGLE_PART", "DISSOLVE_LINES")                     
arcpy.AddMessage(" DONE")    
 
#----------------------------------------------------------------------
# 6. Smooth Merge Polygons 
#----------------------------------------------------------------------
arcpy.AddMessage("6. Smooth Merge Polygons")

if not os.path.exists(os.path.join(dir_dissolve,'Smooth.shp')):
    arcpy.AddMessage(" Smoothing Polygons...")
    smooth_polygons = CA.SmoothPolygon(os.path.join(dir_dissolve,'Dissolve.shp'), os.path.join(dir_dissolve,'Smooth'), "PAEK", tolerance)

arcpy.AddMessage(" DONE") 
#----------------------------------------------------------------------
# 7. Select Pixel polygons and add attributes from Dissolve 
#----------------------------------------------------------------------
arcpy.AddMessage("7. Select Pixel Polygons and Add attributes")
           
for file in shapefiles:
    path, filename = os.path.split(file)
    directory_new = os.path.join(dir_dissolve,filename)
    if file.endswith('Land.shp'):
        if not os.path.exists(os.path.join(dir_temp_pixel_pol,filename)):
            arcpy.AddMessage("  Creating a Land Pixel Polygon file...") 
            arcpy.Select_analysis(os.path.join(dir_dissolve,'Dissolve.shp'),os.path.join(dir_temp_pixel_pol,filename),"\"Class\"='Land'")
      
    if file.endswith('Intertidal.shp'):
        if not os.path.exists(os.path.join(dir_temp_pixel_pol,filename)):
            arcpy.AddMessage("  Creating a Intertidal Pixel Polygon file...") 
            arcpy.Select_analysis(os.path.join(dir_dissolve,'Dissolve.shp'),os.path.join(dir_temp_pixel_pol,filename),"\"Class\"='Intertidal'")
            
    if file.endswith('Reef.shp'):
        if not os.path.exists(os.path.join(dir_temp_pixel_pol,filename)):
            arcpy.Select_analysis(os.path.join(dir_dissolve,'Dissolve.shp'),os.path.join(dir_temp_pixel_pol,filename),"\"Class\"='Reef'")
            arcpy.AddMessage("  Creating a Reef Pixel Polygon file...") 
            
    if file.endswith('feasible.shp'):
        if not os.path.exists(os.path.join(dir_temp_pixel_pol,filename)):
            arcpy.Select_analysis(os.path.join(dir_dissolve,'Dissolve.shp'),os.path.join(dir_temp_pixel_pol,filename),"\"Class\"='NotFeasible'")
            arcpy.AddMessage("  Creating a NotFeasible Pixel Polygon file...") 
                         
        
arcpy.AddMessage(" DONE")    

#----------------------------------------------------------------------
# 8. Select Smooth polygons and add attributes from Dissolve 
#----------------------------------------------------------------------

arcpy.AddMessage("8. Select Smooth Polygons and Add attributes")
        
for file in shapefiles:
    path, filename = os.path.split(file)
    directory_new = os.path.join(dir_dissolve,filename)
    if file.endswith('Land.shp'):
        if not os.path.exists(os.path.join(dir_temp_smooth_pol,filename)):
            arcpy.AddMessage("  Creating a Land Smooth Polygon file...") 
            arcpy.Select_analysis(os.path.join(dir_dissolve,'Smooth.shp'),os.path.join(dir_temp_smooth_pol,filename),"\"Class\"='Land'")
      
    if file.endswith('Intertidal.shp'):
        if not os.path.exists(os.path.join(dir_temp_smooth_pol,filename)):
            arcpy.AddMessage("  Creating a Intertidal Smooth Polygon file...") 
            arcpy.Select_analysis(os.path.join(dir_dissolve,'Smooth.shp'),os.path.join(dir_temp_smooth_pol,filename),"\"Class\"='Intertidal'")
            
    if file.endswith('Reef.shp'):
        if not os.path.exists(os.path.join(dir_temp_smooth_pol,filename)):
            arcpy.Select_analysis(os.path.join(dir_dissolve,'Smooth.shp'),os.path.join(dir_temp_smooth_pol,filename),"\"Class\"='Reef'")
            arcpy.AddMessage("  Creating a Reef Smooth Polygon file...") 
            
    if file.endswith('feasible.shp'):
        if not os.path.exists(os.path.join(dir_temp_smooth_pol,filename)):
            arcpy.Select_analysis(os.path.join(dir_dissolve,'Smooth.shp'),os.path.join(dir_temp_smooth_pol,filename),"\"Class\"='NotFeasible'")
            arcpy.AddMessage("  Creating a NotFeasible Smooth Polygon file...") 
                        
       
arcpy.AddMessage(" DONE")    

#----------------------------------------------------------------------
# 9. Pixel Polygon to Line
#----------------------------------------------------------------------        
arcpy.AddMessage("9. Pixel Polygons to Line")  

for file in os.listdir(dir_temp_pixel_pol):
    if file.endswith('.shp'):
        if not os.path.exists(os.path.join(dir_temp_pixel_line,file)):
            arcpy.PolygonToLine_management(os.path.join(dir_temp_pixel_pol,file), os.path.join(dir_temp_pixel_line,file))
            arcpy.AddMessage("  Creating a pixel line " + file) 
                       
arcpy.AddMessage(" DONE")   

#----------------------------------------------------------------------
# 10. Smooth Polygon to Line
#----------------------------------------------------------------------        
arcpy.AddMessage("10.Smooth Polygons to Line")  
                    
for file in os.listdir(dir_temp_smooth_pol):
    if file.endswith('.shp'):
        if not os.path.exists(os.path.join(dir_temp_smooth_line,file)):
            arcpy.PolygonToLine_management(os.path.join(dir_temp_smooth_pol,file), os.path.join(dir_temp_smooth_line,file))
            arcpy.AddMessage("  Creating a smooth line " + file) 

arcpy.AddMessage(" DONE")  
        
#----------------------------------------------------------------------
# 12. Creating Deliverables
#----------------------------------------------------------------------  

arcpy.AddMessage("10. Creating Deliverables")  

## 1) Land.shp  => Land as polygon

if not os.path.exists(os.path.join(dir_delivery_smooth,"Land.shp")):
    for file in os.listdir(dir_temp_smooth_pol):
        if file.endswith('Land.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_smooth_pol,file), os.path.join(dir_delivery_smooth,"Land.shp"))
    arcpy.AddMessage("  1) Smooth -> Land.shp ")
else:
    arcpy.AddMessage("  1) Smooth -> Land.shp -> Already exists")

if not os.path.exists(os.path.join(dir_delivery_pixel,"Land.shp")):    
    for file in os.listdir(dir_temp_pixel_pol):
        if file.endswith('Land.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_pixel_pol,file), os.path.join(dir_delivery_pixel,"Land.shp"))
    arcpy.AddMessage("  1) Pixel -> Land.shp")
else:
    arcpy.AddMessage("  1) Pixel -> Land.shp -> Already exists")

## 2)Coastline.shp => Land as line

if not os.path.exists(os.path.join(dir_delivery_smooth,"Coastline.shp")):
    for file in os.listdir(dir_temp_smooth_line):
        if file.endswith('Land.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_smooth_line,file), os.path.join(dir_delivery_smooth,"Coastline.shp"))
    arcpy.AddMessage("  2) Smooth -> Coastline.shp ")
else:
    arcpy.AddMessage("  2) Smooth -> Coastline.shp -> Already exists")
    
if not os.path.exists(os.path.join(dir_delivery_pixel,"Coastline.shp")):
    for file in os.listdir(dir_temp_pixel_line):
        if file.endswith('Land.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_pixel_line,file), os.path.join(dir_delivery_pixel,"Coastline.shp"))
    arcpy.AddMessage("  2) Pixel -> Coastline.shp ")
else:
    arcpy.AddMessage("  2) Pixel -> Coastline.shp -> Already exists")
    
## 3)Reef_caution_zone.shp => Merge of land, intertidal and reef as polygon

if not os.path.exists(os.path.join(dir_delivery_smooth,"Reef_caution_zone.shp")):
    caution_list = []
    for file in os.listdir(dir_temp_smooth_pol):
        if file.endswith('Land.shp') or file.endswith('Intertidal.shp') or file.endswith('Reef.shp'):
            caution_list.append(os.path.join(dir_temp_smooth_pol,file)) 
    arcpy.Delete_management(os.path.join(dir_temp_pixel_pol, "Merge.shp")) 
    merge = arcpy.Merge_management(caution_list, os.path.join(dir_temp_smooth_pol, "Merge.shp"))
    arcpy.Dissolve_management(merge, os.path.join(dir_delivery_smooth, "Reef_caution_zone.shp"),"", "","MULTI_PART", "")
    arcpy.Delete_management(os.path.join(dir_temp_smooth_pol, "Merge.shp"))   
    arcpy.AddMessage("  3) Smooth -> Reef_caution_zone.shp ")
else:
    arcpy.AddMessage("  3) Smooth -> Reef_caution_zone.shp -> Already exists")   

if not os.path.exists(os.path.join(dir_delivery_pixel,"Reef_caution_zone.shp")):    
    caution_list = []
    for file in os.listdir(dir_temp_pixel_pol):
        if file.endswith('Land.shp') or file.endswith('Intertidal.shp') or file.endswith('Reef.shp'):
            caution_list.append(os.path.join(dir_temp_pixel_pol,file)) 
    arcpy.Delete_management(os.path.join(dir_temp_pixel_pol, "Merge.shp"))   
    merge = arcpy.Merge_management(caution_list, os.path.join(dir_temp_pixel_pol, "Merge.shp"))
    arcpy.Dissolve_management(merge, os.path.join(dir_delivery_pixel,"Reef_caution_zone.shp"),"", "","MULTI_PART", "")     
    arcpy.Delete_management(os.path.join(dir_temp_pixel_pol, "Merge.shp"))
    arcpy.AddMessage("  3) Pixel -> Reef_caution_zone.shp ")
else:
    arcpy.AddMessage("  3) Pixel -> Reef_caution_zone.shp -> Already exists")  

    
## 4)Reef_caution_zone_edge.shp => Merge of land, intertidal and reef as line

if not os.path.exists(os.path.join(dir_delivery_smooth,"Reef_caution_zone_edge.shp")):
    caution_list = []
    for file in os.listdir(dir_temp_smooth_pol):
        if file.endswith('Land.shp') or file.endswith('Intertidal.shp') or file.endswith('Reef.shp'):
            caution_list.append(os.path.join(dir_temp_smooth_pol,file)) 
    arcpy.Delete_management(os.path.join(dir_temp_smooth_pol, "merge.shp"))
    arcpy.Delete_management(os.path.join(dir_temp_smooth_pol, "dissolve.shp"))
    merge = arcpy.Merge_management(caution_list, os.path.join(dir_temp_smooth_pol, "merge.shp"))
    arcpy.env.XYTolerance = "1 Meters"
    dissolve = arcpy.Dissolve_management(merge, os.path.join(dir_temp_smooth_pol, "dissolve.shp"),"", "","MULTI_PART", "")
    arcpy.PolygonToLine_management(dissolve, os.path.join(dir_delivery_smooth,"Reef_caution_zone_edge.shp"))
    arcpy.Delete_management(os.path.join(dir_temp_smooth_pol, "dissolve.shp"))
    arcpy.Delete_management( os.path.join(dir_temp_smooth_pol, "merge.shp"))
    arcpy.AddMessage("  4) Smooth -> Reef_caution_zone_edge.shp ")
else:
    arcpy.AddMessage("  4) smooth -> Reef_caution_zone_edge.shp -> Already exists")  
    
if not os.path.exists(os.path.join(dir_delivery_pixel,"Reef_caution_zone_edge.shp")):
    caution_list = []
    for file in os.listdir(dir_temp_pixel_pol):
        if file.endswith('Land.shp') or file.endswith('Intertidal.shp') or file.endswith('Reef.shp'):
            caution_list.append(os.path.join(dir_temp_pixel_pol,file))         
    arcpy.Delete_management(os.path.join(dir_temp_pixel_pol, "merge.shp"))
    arcpy.Delete_management(os.path.join(dir_temp_pixel_pol, "dissolve.shp"))
    merge = arcpy.Merge_management(caution_list, os.path.join(dir_temp_pixel_pol, "merge.shp"))
    dissolve = arcpy.Dissolve_management(merge, os.path.join(dir_temp_pixel_pol, "dissolve.shp"),"", "","MULTI_PART", "")
    arcpy.PolygonToLine_management(dissolve, os.path.join(dir_delivery_pixel,"Reef_caution_zone_edge.shp"))
    arcpy.Delete_management(os.path.join(dir_temp_pixel_pol, "dissolve.shp"))
    arcpy.Delete_management( os.path.join(dir_temp_pixel_pol, "merge.shp"))
    arcpy.AddMessage("  4) Pixel -> Reef_caution_zone_edge.shp ")
else:
    arcpy.AddMessage("  4) Pixel -> Reef_caution_zone_edge.shp -> Already exists")    
 
## 5)Reef.shp => Reef as polygon

if not os.path.exists(os.path.join(dir_delivery_smooth,'Reef.shp')):
    for file in os.listdir(dir_temp_smooth_pol):
        if file.endswith('Reef.shp'):
           arcpy.management.CopyFeatures(os.path.join(dir_temp_smooth_pol,file), os.path.join(dir_delivery_smooth,'Reef.shp'))
    arcpy.AddMessage("  5) Smooth -> Reef.shp ")
else:
    arcpy.AddMessage("  5) Smooth -> Reef.shp -> Already exists")   

if not os.path.exists(os.path.join(dir_delivery_pixel,'Reef.shp')):
    for file in os.listdir(dir_temp_pixel_pol):
        if file.endswith('Reef.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_pixel_pol,file), os.path.join(dir_delivery_pixel,'Reef.shp'))
    arcpy.AddMessage("  5) Pixel -> Reef.shp ")
else:
    arcpy.AddMessage("  5) Pixel -> Reef.shp -> Already exists")    
    
## 6)Intertidal.shp => Intertidal as polygon
if not os.path.exists(os.path.join(dir_delivery_smooth,"Intertidal.shp")):
    for file in os.listdir(dir_temp_smooth_pol):
        if file.endswith('Intertidal.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_smooth_pol,file), os.path.join(dir_delivery_smooth,file.split("_")[1]))
    arcpy.AddMessage("  6) Smooth -> Intertidal.shp ")
else:
    arcpy.AddMessage("  6) Smooth -> Intertidal.shp -> Already exists") 

if not os.path.exists(os.path.join(dir_delivery_pixel,"Intertidal.shp")):
    for file in os.listdir(dir_temp_pixel_pol):
        if file.endswith('Intertidal.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_pixel_pol,file), os.path.join(dir_delivery_pixel,file.split("_")[1]))
    arcpy.AddMessage("  6) Pixel -> Intertidal.shp ")
else:
    arcpy.AddMessage("  6) Pixel -> Intertidal.shp -> Already exists")  
    
## 7)Intertidal_edge.shp  => Intertidal and coastline as line

if not os.path.exists(os.path.join(dir_delivery_smooth,"Intertidal_edge.shp")):
    caution_list = []
    for file in os.listdir(dir_temp_smooth_line):
        if file.endswith('Land.shp') or file.endswith('Intertidal.shp'):
            caution_list.append(os.path.join(dir_temp_smooth_pol,file)) 
    arcpy.Delete_management(os.path.join(dir_temp_smooth_pol, "merge.shp"))
    arcpy.Delete_management(os.path.join(dir_temp_smooth_pol, "dissolve.shp"))
    merge = arcpy.Merge_management(caution_list, os.path.join(dir_temp_smooth_pol, "merge.shp"))
    dissolve = arcpy.Dissolve_management(merge, os.path.join(dir_temp_smooth_pol,"dissolve.shp"),"", "","MULTI_PART", "")
    arcpy.PolygonToLine_management(dissolve, os.path.join(dir_delivery_smooth,"Intertidal_edge.shp")) 
    arcpy.Delete_management(os.path.join(dir_temp_smooth_pol, "merge.shp"))
    arcpy.Delete_management(os.path.join(dir_temp_smooth_pol, "dissolve.shp"))
    arcpy.AddMessage("  7) Smooth -> Intertidal_edge.shp ")
else:
    arcpy.AddMessage("  7) Smooth -> Intertidal_edge.shp -> Already exists") 
    
if not os.path.exists(os.path.join(dir_delivery_pixel,"Intertidal_edge.shp")):    
    caution_list = []
    for file in os.listdir(dir_temp_pixel_line):
        if file.endswith('Land.shp') or file.endswith('Intertidal.shp'):
            caution_list.append(os.path.join(dir_temp_pixel_pol,file)) 
    arcpy.Delete_management(os.path.join(dir_temp_pixel_line, "merge.shp"))
    arcpy.Delete_management(os.path.join(dir_temp_pixel_line, "dissolve.shp"))
    merge = arcpy.Merge_management(caution_list, os.path.join(dir_temp_pixel_line, "merge.shp"))
    dissolve = arcpy.Dissolve_management(merge, os.path.join(dir_temp_pixel_line, "dissolve.shp"),"", "","MULTI_PART", "")
    arcpy.PolygonToLine_management(dissolve, os.path.join(dir_delivery_pixel,"Intertidal_edge.shp")) 
    arcpy.Delete_management(os.path.join(dir_temp_pixel_line, "merge.shp"))
    arcpy.Delete_management(os.path.join(dir_temp_pixel_line, "dissolve.shp"))
    arcpy.AddMessage("  7) Pixel -> Intertidal_edge.shp ")
else:
    arcpy.AddMessage("  7) Pixel -> Intertidal_edge.shp -> Already exists") 
    
    
## 8)Not_feasible.shp => Not feasible as polygon  

if not os.path.exists(os.path.join(dir_delivery_smooth,'Not_feasible.shp')):
    for file in os.listdir(dir_temp_smooth_pol):
        if file.endswith('feasible.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_smooth_pol,file), os.path.join(dir_delivery_smooth,'Not_feasible'))
    arcpy.AddMessage("  8) Smooth -> Not_feasible.shp ")
else:
    arcpy.AddMessage("  8) Smooth -> Not_feasible.shp -> Already exists")
    
if not os.path.exists(os.path.join(dir_delivery_pixel,'Not_feasible.shp')):
    for file in os.listdir(dir_temp_pixel_pol): 
        if file.endswith('feasible.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_pixel_pol,file), os.path.join(dir_delivery_pixel,'Not_feasible'))
    arcpy.AddMessage("  8) Pixel -> Not_feasible.shp ")
else:
    arcpy.AddMessage("  8) Pixel -> Not_feasible.shp -> Already exists") 

## 9)Not_feasible_edge.shp => Not feasible as line
 
if not os.path.exists(os.path.join(dir_delivery_smooth,"Not_feasible_edge.shp")):
    for file in os.listdir(dir_temp_smooth_line):
        if file.endswith('feasible.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_smooth_line,file), os.path.join(dir_delivery_smooth,"Not_feasible_edge.shp"))
    arcpy.AddMessage("  9) Smooth -> Not_feasible_edge.shp ")
else:
    arcpy.AddMessage("  9) Smooth -> Not_feasible_edge.shp -> Already exists")
    
if not os.path.exists(os.path.join(dir_delivery_pixel,"Not_feasible_edge.shp")):
    for file in os.listdir(dir_temp_pixel_line):
        if file.endswith('feasible.shp'):
            arcpy.management.CopyFeatures(os.path.join(dir_temp_pixel_line,file), os.path.join(dir_delivery_pixel,"Not_feasible_edge.shp"))
    arcpy.AddMessage("  9) Pixel -> Not_feasible_edge.shp ")
else:
    arcpy.AddMessage("  9) Pixel -> Not_feasible_edge.shp -> Already exists") 
    
#----------------------------------------------------------------------
# XX. Rename Deliverables
#---------------------------------------------------------------------- 

#for file in os.listdir(dir_delivery_pixel):
#    if file.endswith('.shp'):
#        arcpy.AddMessage(file)
#        rename = file.split("_")[1]
#        arcpy.AddMessage(rename)
#        arcpy.Rename_management(os.path.join(dir_delivery_pixel,file), os.path.join(dir_delivery_pixel,rename))

#----------------------------------------------------------------------
# 13. Delete not-needed Fields in Deliverables
#----------------------------------------------------------------------
arcpy.AddMessage("13. Adding fields")  

FieldInsertDir(dir_delivery_pixel,"Version","TEXT","'V01'")   
FieldInsertDir(dir_delivery_pixel,"Date","DATE",'datetime.datetime.now()')   

FieldInsertDir(dir_delivery_smooth,"Version","TEXT","'V01'")   
FieldInsertDir(dir_delivery_smooth,"Date","DATE",'datetime.datetime.now()')       
   
DontDeleteField = ['FID','OID ', 'Shape', 'Class', 'Version', 'Date']
DeleteField(dir_delivery_smooth, DontDeleteField)
DeleteField(dir_delivery_pixel, DontDeleteField)

#for file in os.listdir(dir_delivery_smooth):
#    if file.endswith('Land.shp'):
#        FieldInsertFile(os.path.join(dir_delivery_smooth,file),"Class","TEXT","'Land'")
#    elif file.endswith('Intertidal.shp'):
#        FieldInsertFile(os.path.join(dir_delivery_smooth,file),"Class","TEXT","'Intertidal'")
#    elif file.endswith('Reef.shp'):
#        FieldInsertFile(os.path.join(dir_delivery_smooth,file),"Class","TEXT","'Reef'")
#    elif file.endswith('NotFeasible.shp'):
#        FieldInsertFile(os.path.join(dir_delivery_smooth,file),"Class","TEXT","'NotFeasible'")
#        
#for file in os.listdir(dir_delivery_pixel):
#    if file.endswith('Land.shp'):
#        FieldInsertFile(os.path.join(dir_delivery_pixel,file),"Class","TEXT","'Land'")
#    elif file.endswith('Intertidal.shp'):
#        FieldInsertFile(os.path.join(dir_delivery_pixel,file),"Class","TEXT","'Intertidal'")
#    elif file.endswith('Reef.shp'):
#        FieldInsertFile(os.path.join(dir_delivery_pixel,file),"Class","TEXT","'Reef'")
#    elif file.endswith('NotFeasible.shp'):
#        FieldInsertFile(os.path.join(dir_delivery_pixel,file),"Class","TEXT","'NotFeasible'")
#
#----------------------------------------------------------------------
#---------------- DONE-------------------------------------------------
#----------------------------------------------------------------------  

arcpy.AddMessage(" ")                   
arcpy.AddMessage(" Hey! Completed - Congratulations :o) ")   
arcpy.AddMessage(" ")   
   
    
