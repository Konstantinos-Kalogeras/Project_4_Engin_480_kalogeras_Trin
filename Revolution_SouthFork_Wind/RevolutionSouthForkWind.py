import numpy as np
import py_wake
import geopandas as gpd
from pyproj import Transformer
import matplotlib.pyplot as plt
import pandas as pd
from py_wake.wind_turbines import generic_wind_turbines
from py_wake import NOJ
from py_wake.site._site import UniformWeibullSite, PowerShear
from py_wake.flow_map import HorizontalGrid

class RevolutionWind:
    def __init__(self):
        geojson_path = 'E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\Revolution_SouthFork_Wind\revolution_shouth_fork_turbine_position.geojson'
        self.geojson_path = geojson_path
        self.x = None
        self.y = None


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
    def get_coordinates(self):
        return self.x, self.y
    

class RevolutionWindBoundatrys:
    def __init__(self):
        geojson_path = 'E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\Revolution_SouthFork_Wind\south_fork_boundarys.geojson'
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
    

class SG_11200(generic_wind_turbines):
    def __init__(self):
        """
        paramiters
        __________
        The turbulance intesity varies around 6-8%
        """
        generic_wind_turbines.__init__(self, name = 'SG 11-200', diameter = 200,hub_height = 100,
                                       Power_norm = 11000, turbulance_intesity = 0.07)


class RevolutionWindData(UniformWeibullSite):
    def __init__(self, ti= 0.07, shear=PowerShear(h_ref=100, alpha = 0.1)):
        f = [ 652.94 ,  745.53  , 622.32   ,588.86  , 474.39  , 456.32  ,
              717.71,  1225.30  ,1385.41,  1037.11,  1158.19   ,935.93]
        a = [     9.93  ,  10.64  ,   9.87    , 8.85  ,   8.46 ,    8.26 ,
                10.45  ,  11.75  ,  11.40   , 10.82 ,   11.95 ,   10.08]
        k = [2.385  ,  1.822  ,  1.979 ,   1.842  ,  1.607  ,  1.486  ,
               1.865  ,  2.256  ,  2.678  ,  2.170 ,   2.455  ,  2.506]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti,ti, shear=shear)
        self.initial_position = np.array([site.x, site.y]).T
        self.name = 'Reovolution South Fork Wind'



site = RevolutionWind()
boundary = RevolutionWindBoundatrys()
WindRoseData = RevolutionWindData()
Turbine = SG_11200()


# sim_res = NOJ(site, Turbine)
site.convert_to_utm()
boundary_x, boundary_y = zip(*boundary.get_utm())

sim_res = NOJ(site, Turbine)

electrical_power = sim_res(site.x, site.y).power

aep = sim_res(site.x,site.y).aep().sum()

print('Total AEP production: ',aep, 'GW')


            
