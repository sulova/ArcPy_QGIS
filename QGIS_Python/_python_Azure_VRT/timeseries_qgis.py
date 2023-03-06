import os
from dateutil import rrule
from string import Template
from osgeo import gdal
from qgis.processing import alg

date_start = dt.datetime(2021,6,1)
date_end = dt.datetime(2021,9, 30)

product = "TSEB_PT_20m_ET_day_gf"
vrt_filename = rf"C:\Users\ansu\Documents\{product}.vrt"
container = "ccc-storage"
template_path = Template("ET/output/20m/germany_sw/germany_sw_${year}${month}${day}_${product}.tif")
azure_connection_string = "DefaultEndpointsProtocol=https;AccountName=ccubed;AccountKey=b284EE1qXogSUEhsCmb3Z9m2YrcCGW3m+PsRdMlhguCOVLRoJKA+s6vQL61kMv/5mpUH5MFUsJczH8Dgo5jxhA==;EndpointSuffix=core.windows.net"

def virtual_blob_timestack(date_start, date_end, product, vrt_filename, container, template_path, azure_connection_string):
    """
    Create a GDAL virtual raster from COGs stored in blob in a well structured folder structure
    """
    os.environ["AZURE_STORAGE_CONNECTION_STRING"] = azure_connection_string
    
    file_list = []
    for date in rrule.rrule(dtstart=date_start, until=date_end, freq=rrule.DAILY):
        key = template_path.substitute(year=f"{date:%Y}",
                                       month=f"{date:%m}",
                                       day=f"{date:%d}",
                                       product=f"{product}")
        file_list.append(f"/vsiaz/{container}/{key}")
        print(key)
    gdal.BuildVRT(vrt_filename, file_list, separate=True)



virtual_blob_timestack(date_start,
                           date_end,
                           product,
                           vrt_filename,
                           container,
                           template_path,
                           azure_connection_string)
