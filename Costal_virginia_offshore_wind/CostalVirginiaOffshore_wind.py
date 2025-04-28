import numpy as np
import py_wake
import geopandas as gpd
from pyproj import Transformer
import matplotlib.pyplot as plt
import pandas as pd
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine
# from py_wake import NOJ
from py_wake.site._site import UniformWeibullSite, PowerShear
from py_wake.flow_map import HorizontalGrid
from py_wake.literature.gaussian_models import Bastankhah_PorteAgel_2014

class CostalVirginia:
    def __init__(self):
        geojson_path = 'E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\Costal_virginia_offshore_wind\costalvirginiawindposistions.geojson'
        self.geojson_path = geojson_path
        # self.x = None
        # self.y = None


    def convert_to_utm(self):
        gdf = gpd.read_file(self.geojson_path)
        gdf = gdf.to_crs(epsg=4326)


        lon_list = []
        lat_list = []

        for geom in gdf.geometry:
            lon, lat = geom.x, geom.y
            lon_list.append(lon)
            lat_list.append(lat)

        transformer = Transformer.from_crs('EPSG:4326', 'EPSG:32619', always_xy =True)
        utm_x, utm_y = [],[]

        for lon, lat in zip(lon_list, lat_list):
            x, y = transformer.transform(lon, lat)
            utm_x.append(x)
            utm_y.append(y)


        self.x = np.array(utm_x)
        self.y = np.array(utm_y)
    # def get_coordinates(self):
        return self.x, self.y
    

class CostalVirginiaBoundatrys:
    def __init__(self):
        geojson_path = 'E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\Costal_virginia_offshore_wind\costalvirginiaboundary.geojson'
        self.gdf = gpd.read_file(geojson_path)

        if self.gdf.crs is None:
            self.gdf.set_crs(epsg=4326, inplace = True)

        self.latlon_coords = np.array(self.gdf.geometry.iloc[0].coords)

    def _get_utm_crs(self):
        centroid = self.gdf.geometry.centroid.iloc[0]       
        lon = centroid.x
        utm_zone = int((lon + 180) / 6) + 1
        return f"EPSG:{32600 + utm_zone}"

    def get_latlon(self):
        return self.latlon_coords

    def get_utm(self):
        return self.utm_coords
    

class SG_14222(GenericWindTurbine):
    def __init__(self):
        """
        paramiters
        __________
        The turbulance intesity varies around 6-8%
        """
        # GenericWindTurbine.__init__(self, name = 'SG 14.0-222DD', diameter = 222,hub_height = 150,
        #                                Power_norm = 14000, turbulance_intesity = 0.07)
        GenericWindTurbine.__init__(self, name='SG 14.0-222DD', diameter=222, hub_height=150, 
                                    power_norm=14000, turbulence_intensity=0.07)


class CostalVirginiaData(UniformWeibullSite):
    def __init__(self, ti= 0.07, shear=PowerShear(h_ref=150, alpha = 0.1)):
        f = [ 9.1938, 9.9099, 9.0817, 5.2505, 4.8252, 5.7245, 
             11.491, 14.2491, 9.3086, 5.06, 6.4652, 9.4405]
        a = [10.50   ,  9.94   ,  8.96    , 8.22  ,   7.34,     7.94 ,
                11.27,   13.33  ,  11.86 ,   10.03  ,  10.26  ,  11.12]
        k = [2.260  ,  2.139   , 1.971  ,  1.771  ,  1.521  ,  1.514,
             1.955 ,   2.568  ,  2.775 ,   2.049 ,   1.951  ,  2.295]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        # self.initial_position = np.array([site.x, site.y]).T
        self.name = 'Reovolution South Fork Wind'


x,y = CostalVirginia().convert_to_utm()

site = CostalVirginiaData()
# boundary = CostalVirginiaBoundatrys()
# WindRoseData = CostalVirginiaData()
Turbine = SG_14222()


# sim_res = NOJ(site, Turbine)
# site.convert_to_utm()
# boundary_x, boundary_y = zip(*boundary.get_utm())

sim_res = Bastankhah_PorteAgel_2014(site, Turbine, k = 0.0324555)

electrical_power = sim_res(x,y).Power

aep = sim_res(x,y).aep().sum()

print('Total AEP production for Costal Virginia Offshore Wind site: ',aep, 'MW')


            
