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

class EnedoLuchterdunen:
    def __init__(self):
        geojson_path = 'E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\Eneco_Luchterdunen\eneco_lutherduinen_turbine_coordinates.geojson'
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
    

class EnedoLuchterdunenBoundatrys:
    def __init__(self):
        geojson_path = 'E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\Eneco_Luchterdunen\eneco_luchterduinen_boundary.geojson'
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
    

class V_1123(generic_wind_turbines):
    def __init__(self):
        """
        paramiters
        __________
        The turbulance intesity varies around 6-8%
        """
        generic_wind_turbines.__init__(self, name = 'SG 14.0-222DD', diameter = 112,hub_height = 100,
                                       Power_norm = 3000, turbulance_intesity = 0.07)


class EnedoLuchterdunenData(UniformWeibullSite):
    def __init__(self, ti= 0.07, shear=PowerShear(h_ref=100, alpha = 0.1)):
        f = [ 580.07 ,  615.57  , 622.08,   648.58,   547.10,   547.41,
            779.38,  1328.15 , 1680.45,  1047.52 ,  868.37 ,  735.32 ]
        a = [7.95 ,    9.00 ,   9.45  ,  10.41 ,    8.87 ,    9.33   ,
              11.30 ,   12.62  ,  12.07   , 11.04   ,  9.49  ,   9.34]
        k = [2.002  ,  2.436 ,   2.662   , 2.533,    2.244,    2.291  ,
               2.205 ,   2.432 ,  2.260    ,2.127 ,   2.174,    2.068]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti,ti, shear=shear)
        self.initial_position = np.array([site.x, site.y]).T
        self.name = 'Reovolution South Fork Wind'



site = EnedoLuchterdunen()
boundary = EnedoLuchterdunenBoundatrys()
WindRoseData = EnedoLuchterdunenData()
Turbine = V_1123()


# sim_res = NOJ(site, Turbine)
site.convert_to_utm()
boundary_x, boundary_y = zip(*boundary.get_utm())

sim_res = NOJ(site, Turbine)

electrical_power = sim_res(site.x, site.y).power

aep = sim_res(site.x,site.y).aep().sum()

print('Total AEP production: ',aep, 'GW')


            
