import arcpy
import os
import math
from arcpy.sa import *

overwriteOutput = True
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'SDB_Template.aprx')

# Open the ARCgis Pro project
aprx = arcpy.mp.ArcGISProject(filename)
maps = aprx.listMaps("SDB*")[0]

# Apply the SDB extent to the mapframe 
print("1.Working on the view of map frame ")    
layout = aprx.listLayouts()[0]

layer_SDB = maps.listLayers("SDB Depth [m]")[0]
mf = layout.listElements("mapframe_element", "SDB_MF")[0]

layer_extent = mf.getLayerExtent(layer_SDB, True)
mf.camera.setExtent(layer_extent)

# Extract sdb values to points
print("2.Extract sdb values to points")  

layer_ICESat = maps.listLayers("ICESat-2")[0]

# Delete the ICESAT_Depth file
if os.path.exists(os.path.join(dirname,'Inputs/ICESAT_Depth.shp')):
   arcpy.Delete_management(os.path.join(dirname,'Inputs/ICESAT_Depth.shp'))

# Extract values of the sbd to points
fieldnames = [field.name for field in arcpy.ListFields(layer_ICESat)]

myfield = "RASTERVALU"

if  myfield in fieldnames:
    layer_Depth = os.path.join(dirname, 'Inputs/ICESAT_Depth.shp')
    arcpy.management.CopyFeatures(layer_ICESat, layer_Depth)
else:
    layer_Depth = os.path.join(dirname, 'Inputs/ICESAT_Depth.shp')
    ExtractValuesToPoints(layer_ICESat, layer_SDB, layer_Depth)
   
layer_Depth_icesat = maps.listLayers("ICESat-2 Depth*")[0]     

# Scale up the icesat legend
if layer_ICESat.isFeatureLayer:
  sym = layer_ICESat.symbology
  if hasattr(sym, 'renderer'):
    
    if sym.renderer.type == 'UnclassedColorsRenderer':
    
      # Modify basic properties
      
      sym.renderer.field = "depth"
      sym.renderer.lowerLabel =  str(math.ceil(float(sym.renderer.lowerLabel)))
      sym.renderer.upperLabel =  str(math.floor(float(sym.renderer.upperLabel)))
      print("3.Creating the ICESat-2 labels:", sym.renderer.lowerLabel,"and",sym.renderer.upperLabel ) 
      
      # Modify the Icesat-2 template
      
      symTemp = sym.renderer.symbolTemplate
      symTemp.applySymbolFromGallery('ICE')
      sym.renderer.updateSymbolTemplate(symTemp)
      layer_Depth_icesat.symbology = sym  
 
# Scale up the SDB legend
if layer_SDB.isRasterLayer:

  sym = layer_SDB.symbology 
  sym.updateColorizer ('RasterClassifyColorizer')
  sym.updateColorizer ('RasterStretchColorizer')
  
  if hasattr(sym, 'colorizer'):  
    if sym.colorizer.type == 'RasterStretchColorizer':
        sym.band = 1        
        cr = aprx.listColorRamps('Bathymetry #2')[0]
        sym.colorizer.colorRamp = cr
        sym.colorizer.minLabel = str(round(float(sym.colorizer.minLabel)))
        sym.colorizer.maxLabel = str(round(float(sym.colorizer.maxLabel)))
        print("4.Creating the SDB labels:", sym.colorizer.minLabel,"and" ,sym.colorizer.maxLabel) 
        
        layer_SDB.symbology = sym
       
aprx.save()

# Expor to a png file
print("5.Exporting the file") 

layout.exportToPNG(os.path.join(dirname,'Output/SDB_Report'),resolution = 200)

print("6.The report is saved:",os.path.join(dirname,'Output/SDB_Report')) 