import numpy as np
import geopandas as gpd
from pyproj import Transformer
import matplotlib.pyplot as plt


##################################### This is a project that was developed for project 3 and has nothing to do with project 4 ################################

class EnicoLuchterduinion_site:
    
    def __init__(self, geojson_path):  
        # stores the path to file
        self.geojson_path = geojson_path
        # initiates place holders for UTM coordinates
        self.x = None
        self.y = None

    def convert_to_utm(self):
        # Reads coordinates from file
        gdf = gpd.read_file(self.geojson_path)

        # Converts coordinates to WGS84 (long/lat) for consistancy
        gdf = gdf.to_crs(epsg = 4326)

        # Extracts coordinates from the first geomitry (assumes LineString)
        coordinates = gdf.geometry[0].coords

        # seperates the list into lat and long
        lon_list, Lat_list = zip(*coordinates)

        # creates a transformer to conver from WGS82 (EPSG:4362) to UTM zome 32N (EPSG:32632)
        transformer = Transformer.from_crs('EPSG:4326', 'EPSG:32632', always_xy=True)

        # preparing list to store UTM coordinates
        utm_x, utm_y = [],[]

        # converting each coordinate pair using the transformer
        for lon, lat in zip(lon_list, Lat_list):
            x, y = transformer.transform(lon,lat) # performing convertion
            utm_x.append(x) # appending to the repective list
            utm_y.append(y)

        # store reults into Numpy arrays
        self.x = np.array(utm_x)
        self.y = np.array(utm_y)

    def get_coordinates(self):
        # Return the UTM coordinates as a tuple of Numpy Arrays
        return self.x, self.y
