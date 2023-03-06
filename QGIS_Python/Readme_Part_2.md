# Python programming basics in QGIS VOl 1

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


