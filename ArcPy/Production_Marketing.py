import arcpy
import os
from arcpy.sa import *

overwriteOutput = True

# gain the path to the project directory
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'SDB_Template_Marketing.aprx')

# open the Arcgis Pro project
aprx = arcpy.mp.ArcGISProject(filename)

# delete previous "ICESAT_Depth"shp
arcpy.Delete_management(os.path.join(dirname,'Inputs/ICESAT_Depth.shp'))

print("1.Input data:") 

# Open layout, maps and layers
layout = aprx.listLayouts()[1]
print ("  Layout:", layout.name)

map_2D = aprx.listMaps("SDB_2D")[0]
print ("  2D Map:", map_2D.name)

layer_SDB_2D = map_2D.listLayers("SDB Depth*")[0]
print ("  SDB Layer (2D):", layer_SDB_2D.name)

map_3D = aprx.listMaps("SDB_3D")[0]
print ("  3D Map:", map_3D.name)

layer_SDB_3D = map_3D.listLayers("SDB Depth*")[0]
print ("  SDB Layer (3D):", layer_SDB_3D.name)

layer_Depth_icesat = map_3D.listLayers("ICESat-2 Depth*")[0]
print ("  ICESat-2 Layer (3D):", layer_Depth_icesat.name)

# Extract values of the sbd to points

print("2.Extract sdb values to points")  
layer_ICESat = map_3D.listLayers("ICESat-2")[0]
fieldnames = [field.name for field in arcpy.ListFields(layer_ICESat)]

myfield = "RASTERVALU"

if  myfield in fieldnames:
    layer_Depth = os.path.join(dirname, 'Inputs/ICESAT_Depth.shp')
    arcpy.management.CopyFeatures(layer_ICESat, layer_Depth)
else:
    layer_Depth = os.path.join(dirname, 'Inputs/ICESAT_Depth.shp')
    ExtractValuesToPoints(layer_ICESat, layer_SDB_3D, layer_Depth)
 
print("  Done") 
  

# Working on the layer extent for the 2D map
print("3.Working on the 2D extent:")   

mf_2D = layout.listElements("mapframe_element", "SDB_2D")[0]
print("  Map Frame 2D:", mf_2D.name)

layer_extent_2D = mf_2D.getLayerExtent(layer_SDB_2D, True)
mf_2D.camera.setExtent(layer_extent_2D) 

# Working on the layer extent for the 3D map
print("3.Working on the 3D extent:")   

mf_3D = layout.listElements("mapframe_element", "SDB_3D")[0]
print("  Map Frame 3D:", mf_3D.name)

#layer_extent_3D = mf_3D.getLayerExtent(layer_SDB_3D, True)
#mf_3D.camera.setExtent(layer_extent_2D) 

#mf_3D.setExtent(layer_extent_2D) 
mf_3D.panToExtent(layer_extent_2D) 

# Working on the legend
if layer_ICESat.isFeatureLayer:
  sym = layer_ICESat.symbology
  if hasattr(sym, 'renderer'):
    if sym.renderer.type == 'UnclassedColorsRenderer':
      #modify basic properties
      sym.renderer.field = "depth"
      sym.renderer.lowerLabel =  str(math.ceil(float(sym.renderer.lowerLabel)))
      sym.renderer.upperLabel =  str(math.floor(float(sym.renderer.upperLabel)))
      print("4.Creating the ICESat-2 labels:", sym.renderer.lowerLabel,"and",sym.renderer.upperLabel ) 
      
      #Modify the symbol template
      symTemp = sym.renderer.symbolTemplate
      symTemp.applySymbolFromGallery('ICE')
      sym.renderer.updateSymbolTemplate(symTemp)
      layer_Depth_icesat.symbology = sym  
 

if layer_SDB_3D.isRasterLayer:
  sym = layer_SDB_3D.symbology 
  sym.updateColorizer ('RasterClassifyColorizer')
  sym.updateColorizer ('RasterStretchColorizer')
  if hasattr(sym, 'colorizer'):  
    if sym.colorizer.type == 'RasterStretchColorizer':
        sym.band = 1        
        cr = aprx.listColorRamps('Bathymetry #2')[0]
        sym.colorizer.colorRamp = cr
        sym.colorizer.minLabel = str(round(float(sym.colorizer.minLabel)))
        sym.colorizer.maxLabel = str(round(float(sym.colorizer.maxLabel)))
        print("5.Working on the SDB labels:", sym.colorizer.minLabel,"and" ,sym.colorizer.maxLabel) 
        
        layer_SDB_3D.symbology = sym
       
aprx.save()

#layout = aprx.listLayouts()[0]

#Expor to a png file
print("5.Exporting...") 
layout.exportToPNG(os.path.join(dirname,'Output/SDB_Report'),resolution = 200)
print("6.Done") 