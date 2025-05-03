import numpy as np
import py_wake
import geopandas as gpd
from pyproj import Transformer
import matplotlib.pyplot as plt
import pandas as pd
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine
from py_wake.literature.gaussian_models import Bastankhah_PorteAgel_2014
from py_wake.site._site import UniformWeibullSite, PowerShear



# Class to handle the turbine positions
class VinyardWind_1():
    def __init__(self):
        # Hardcoded path to turbine positions GeoJSON
        geojson_path = "E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/posistions_of_Vinyard_wind_1_terbines.geojson"
        self.geojson_path = geojson_path


    def convert_to_utm(self):
        gdf = gpd.read_file(self.geojson_path)
        gdf = gdf.to_crs(epsg=4326)

 
        lon_list = []
        lat_list = []

        for geom in gdf.geometry:
            lon, lat = geom.x, geom.y
            lon_list.append(lon)
            lat_list.append(lat)

        transformer = Transformer.from_crs('EPSG:4326', 'EPSG:32619', always_xy=True)
        utm_x, utm_y = [], []

        for lon, lat in zip(lon_list, lat_list):
            x, y = transformer.transform(lon, lat)
            utm_x.append(x)
            utm_y.append(y)

        self.x = np.array(utm_x)
        self.y = np.array(utm_y)
     

        return self.x,self.y


    
x, y = VinyardWind_1().convert_to_utm()

print('done')
    
class Haliade_X(GenericWindTurbine):
    def __init__(self):
        """
        paramiters
        __________
        The turbulance intesity varies around 6-8%
        """
        GenericWindTurbine.__init__(self, name='Haliade-X', diameter=220, hub_height=150, 
                                    power_norm=13000, turbulence_intensity=0.07)

class VinyardWind2(UniformWeibullSite):
    def __init__(self, ti=0.07, shear=PowerShear(h_ref=150, alpha=0.1)):
        f =[6.4452, 7.6731, 6.4753, 6.0399, 4.8786, 
             4.5063, 7.318, 11.7828, 13.0872, 11.1976, # this lisrt was multiplied by 0.01 using chatGpt
            11.1351, 9.461]
        a = [10.26,    10.44,     9.52,     8.96,     9.58,
             9.72,    11.48 ,   13.25,    12.46,    11.40,    12.35,    10.48]
        k = [ 2.225,    1.697,    1.721,    1.689 ,   1.525  ,  1.498 ,
                1.686,    2.143 ,   2.369   , 2.186    ,2.385   , 2.404]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        # self.initial_position = np.array([site.x, site.y]).T
        self.name = 'Vinyard Wind Farm'

x, y = VinyardWind_1().convert_to_utm()

print('done')
    
# Main execution
site = VinyardWind2()

Turbine = Haliade_X()

sim_res = Bastankhah_PorteAgel_2014(site, Turbine, k = 0.0324555)




electrical_power = sim_res(x, y).Power



aep = sim_res(x,y).aep().sum()

print('Total AEP production for Vinyard Wind 1 site: ',aep, 'MW')

