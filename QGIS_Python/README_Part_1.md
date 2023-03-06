# Python programming basics in QGIS

This repository aims to outline Python programming language in QGIS and keep it short and relevant to get a solid foundation for visualizing and analyzing data.

PyQgis cookbook can be found [here](https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/).

It is great for users who do not have any prior programming knowledge and they want to build their knowledge gradually in QGIS. 

*1) Python script to open a preexisting QGIS project named as .qgz*
```python
project = QgsProject.instance()
project.read("C:\\Users\\sulova andrea\\Desktop\\Courses\\ProjectName.qgz")
```

*2) To load a vector layer is selected the Coordinate Reference System WGS84 (EPSG: 4326)*
```python
QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(4326))

# Add vector data "Roads" and "OGR" means datatype. 
layer = iface.addVectorLayer("C:\\Users\\sulova andrea\\Desktop\\Courses\\ROAD.shp","Roads","ogr")

# Add raster data "Aerials" 
layer = iface.addRasterLayer("C:\\Users\\sulova andrea\\Desktop\\Courses\\IMO.ecw","Aerials")

# set the color to green
layer.renderer().symbol().setColor(QColor("green"))

# the road layer will be triggered a repaint, meaning it to manually refresh the screen so you can see that the color
layer.triggerRepaint()
```

*3) Buffer (temp_location)*
```python
# A temporary location
bufferloc = "C:\\temp\\mybuffer.shp"

# Creating the buffer of 3m distance using the road centerlines
processing.run("native:buffer", {'INPUT':'C:\\Users\\sulova andrea\\Desktop\\Courses\\ROAD_CENTERLINES.shp',
'DISTANCE':3,
'SEGMENTS':5,
'END_CAP_STYLE':0,
'JOIN_STYLE':0,
'MITER_LIMIT':2,
'DISSOLVE':False,
'OUTPUT':bufferloc})

# Add buffer saved as "bufferlo"as a layer in project named "(3M)"
iface.addVectorLayer(bufferloc,"(3M)","ogc")
```

*4) Save layer definition*
```python
#Open Current Project
myInstance = QgsProject.instance()

#layer name 'ROAD_CENTERLINES' open in project is given to 'road_layer'
road_layer = myInstance.mapLayersByName('ROAD_CENTERLINES')[0]
root = myInstance.layerTreeRoot()

# find an id of layer root 
myLayer=root.findLayer(road_layer.id())

# Export the layer definition into a dictionary
QgsLayerDefinition().exportLayerDefinition("C:\\Users\\sulova andrea\\Desktop\\Courses\\test.qlr",[myLayer])
```

*5) Save a working project* 
```python
project.write("C:\\Users\\sulova andrea\\Desktop\\Courses\\streetlight_map_new.qgz")
QgsProject.instance().clear()
```

*6) Set CrsProj(26910) of the open project*
```python
crs = QgsCoordinateReferenceSystem(26910)
QgsProject.instance().setCrs(crs)
```

*7) Set a new coordinate projection for an open project*
```python
proj4 = "+proj=utm +zone=10 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"
crs = QgsCoordinateReferenceSystem()
crs.createFromProj4(proj4)
QgsProject.instance().setCrs(crs)
```

*8) Set a new coordinate projection using WKT for an open project*

```python
# Well-known text (WKT) is a text markup language for representing vector geometry objects. 
wkt = 'PROJCS["NAD83 / UTM zone 10N",GEOGCS\
["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.257222101,\
AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0,\
AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],\
AUTHORITY["EPSG","4269"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],\
PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],\
PARAMETER["central_meridian",-123],PARAMETER["scale_factor",0.9996],\
PARAMETER["false_easting",500000],PARAMETER["false_northing",0],\
AUTHORITY["EPSG","26910"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
crs = QgsCoordinateReferenceSystem(wkt)
QgsProject.instance().setCrs(crs)
```
