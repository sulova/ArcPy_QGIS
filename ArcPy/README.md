## Arcpy
*ArcPy is a site-package and  provides access to geoprocessing tools as well as additional functions, classes, and modules that allow you to create simple or complex workflows quickly and easily..*

- With ArcPy, you’ve access to the:
1) Geoprocessing tools – Extensions 
2) Functions 
3) Classes

**ArcPy Functions**
Functions perform a specific task as a part of larger program.
All geoprocessing tools are functions -- Union, Buffer, Clip etc., but not all functions are geoprocessing tools -- List datasets, describe dataset, create cursor

**ArcPy Classes**
Classes provide a framework for creating object - referred to as an instance.
Examples of classes - SpatialReference, Extent etc. 
Classes have methods & properties -- Spatialreference.name -Spatialreference.type

**ArcPy Modules**
Modules are Python libraries containing functions and classes  
- Mapping modules: arcpy.mapping 
- Spatial Analyst module: arcpy.sa 
- Geostatistical module: arcpy.ga 

Example:
**Check inputs**

```python
arcpy.AddMessage("1. Check input files: ")

Land = arcpy.GetParameterAsText(0)
Tide = arcpy.GetParameterAsText(1)
Reef = arcpy.GetParameterAsText(2)
Feasible = arcpy.GetParameterAsText(3)

tolerance = arcpy.GetParameterAsText(4)
if tolerance == '#' or not tolerance:
   tolerance = 50

files = [Land,Tide,Reef,Feasible]
file_name = ['Land','Tide','Reef','Feasible']
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

```

Examples:
**Creates a unique list of field values based on a feature class and field name**
```python
import arcpy
featureclass = "C:/data/county.gdb/hospital"
field = "Zip"

valueList = []
rows = arcpy.da.SearchCursor(featureclass, [field])
for row in rows:
    valueList.append(row[0])

uniqueSet = set(valueList)
uniqueList = list(uniqueSet)
uniqueList.sort()

print(uniqueList)
```

**Select Polygons using a attribute value**
```python
arcpy.AddMessage("Select Polygons using attributes values")
           
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
```
