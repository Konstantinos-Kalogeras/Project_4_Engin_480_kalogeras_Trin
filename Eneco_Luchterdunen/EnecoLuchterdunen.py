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

######################################################################################################################################
############################# This project was developed with the help of Prof. Rafael Vallota Rodrigues #############################
######################################################################################################################################

######################################################################################################################################
############################# Developer: Konstantinos Kalogeras ###################################################################### 
############################# Project Partner: Dat Trinh #############################################################################
######################################################################################################################################

class EnedoLuchterdunen:
    def __init__(self):
        geojson_path = 'E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\Eneco_Luchterdunen\eneco_lutherduinen_turbine_coordinates.geojson'
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
    

class V_1123(GenericWindTurbine):
    def __init__(self):
        """
        paramiters
        __________
        The turbulance intesity varies around 6-8%
        """
        # GenericWindTurbine.__init__(self, name = 'V_1123', diameter = 112,hub_height = 100,
                                    #    Power_norm = 3000, turbulance_intesity = 0.07)
        GenericWindTurbine.__init__(self, name='V_11-23', diameter=112, hub_height=100, 
                                    power_norm=3000, turbulence_intensity=0.07)


class EnedoLuchterdunenData(UniformWeibullSite):
    def __init__(self, ti= 0.07, shear=PowerShear(h_ref=100, alpha = 0.1)):
        f = [ 5.8007, 6.1557, 6.2208, 6.4858, 5.471, 5.4741, 
             7.7938, 13.2815, 16.8045, 10.4752, 8.6837, 7.3532]
        a = [7.95 ,    9.00 ,   9.45  ,  10.41 ,    8.87 ,    9.33   ,
              11.30 ,   12.62  ,  12.07   , 11.04   ,  9.49  ,   9.34]
        k = [2.002  ,  2.436 ,   2.662   , 2.533,    2.244,    2.291  ,
               2.205 ,   2.432 ,  2.260    ,2.127 ,   2.174,    2.068]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        # self.initial_position = np.array([site.x, site.y]).T
        self.name = 'Reovolution South Fork Wind'

x,y = EnedoLuchterdunen().convert_to_utm()

site = EnedoLuchterdunenData()
# boundary = EnedoLuchterdunenBoundatrys()
# WindRoseData = EnedoLuchterdunenData()
Turbine = V_1123()


# sim_res = NOJ(site, Turbine)
# site.convert_to_utm()
# boundary_x, boundary_y = zip(*boundary.get_utm())

sim_res = Bastankhah_PorteAgel_2014(site, Turbine, k = 0.0324555)

electrical_power = sim_res(x,y).Power

aep = sim_res(x,y).aep().sum()

print('Total AEP production for Enedo Luchterndunen site: ',aep, 'GW')


            
