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


# class Vinyard1WindRoseData:
#     def __init__(self):
#         self.csv_path = "E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/windPowerRose.csv"
        
#         self.wd = None  # Wind directions
#         self.freq = None  # Frequencies
        
#         self._load_data()

#     def _load_data(self):
#         df = pd.read_csv(self.csv_path)

#         # Debug: print the columns
#         print("Columns in CSV:", df.columns)

#         # Get the center degrees (wind direction) and value (frequency)
#         self.wd = df['center_degrees'].to_numpy()
#         self.freq = df['value'].to_numpy()

#     def get_data(self):
#         """
#         Returns a tuple: (wind_directions, frequency)
#         """
#         return self.wd, self.freq






# Class to handle the turbine positions
class VinyardWind_1:
    def __init__(self):
        # Hardcoded path to turbine positions GeoJSON
        geojson_path = "E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/posistions_of_Vinyard_wind_1_terbines.geojson"
        self.geojson_path = geojson_path
        self.x = None
        self.y = None

    def convert_to_utm(self):
        gdf = gpd.read_file(self.geojson_path)
        gdf = gdf.to_crs(epsg=4326)

        # Extracting Point coordinates from all geometries
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

    def get_coordinates(self):
        return self.x, self.y


# Class to handle the project boundary
class Vinyard_wind_boundarys:
    def __init__(self):
        # Hardcoded path to boundary GeoJSON
        geojson_path = "E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/outer_boundary_vinyard_wind_1.geojson"
        self.gdf = gpd.read_file(geojson_path)

        if self.gdf.crs is None:
            self.gdf.set_crs(epsg=4326, inplace=True)

        self.latlon_coords = np.array(self.gdf.geometry.iloc[0].coords)
        utm_crs = self._get_utm_crs()
        self.gdf_utm = self.gdf.to_crs(utm_crs)
        self.utm_coords = np.array(self.gdf_utm.geometry.iloc[0].coords)

    def _get_utm_crs(self):
        centroid = self.gdf.geometry.centroid.iloc[0]
        lon = centroid.x
        utm_zone = int((lon + 180) / 6) + 1
        return f"EPSG:{32600 + utm_zone}"

    def get_latlon(self):
        return self.latlon_coords

    def get_utm(self):
        return self.utm_coords
    
class Haliade_X(generic_wind_turbines):
    def __init__(self):
        """
        paramiters
        __________
        The turbulance intesity varies around 6-8%
        """
        generic_wind_turbines.__init__(self, name='Haliade-X', diameter=220, hub_height=150, 
                                    power_norm=13000, turbulance_intesity=0.07)

class VinyardWind1(UniformWeibullSite):
    def __init__(self, ti=0.07, shear=PowerShear(h_ref=150, alpha=0.1)):
        f = [644.52,   767.31,   647.53,   603.99,   487.86,   
             450.63,   731.80,  1178.28,  1308.72,  1119.76,  1113.51,   946.10]
        a = [10.26,    10.44,     9.52,     8.96,     9.58,
             9.72,    11.48 ,   13.25,    12.46,    11.40,    12.35,    10.48]
        k = [ 2.225,    1.697,    1.721,    1.689 ,   1.525  ,  1.498 ,
                1.686,    2.143 ,   2.369   , 2.186    ,2.385   , 2.404]
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)
        self.initial_position = np.array([site.x, site.y]).T
        self.name = 'Vinyard Wind Farm'

# Main execution
site = VinyardWind_1()
boundary = Vinyard_wind_boundarys()
wind_rose_data = VinyardWind1()
Turbine = Haliade_X()

sim_res = NOJ(site, Turbine)
site.convert_to_utm()
x, y = site.get_coordinates()
boundary_x, boundary_y = zip(*boundary.get_utm())

sim_res = NOJ(site, Turbine)

electrical_power = sim_res(x, y).Power

# electrical_power.isel(wt = 2, wd = 330, ws = 7)

aep = sim_res(x,y).aep().sum()

print('Total AEP production: ',aep, 'GW')

# Plotting quordinates with boundarys of site 
plt.figure(figsize=(10, 8))
plt.scatter(x, y, color='green', label='Turbine Positions')
plt.plot(boundary_x, boundary_y, color='blue', label='Project Boundary')
plt.title("Vineyard Wind 1 - UTM Coordinates")
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.grid(True)
plt.legend()
plt.axis("equal")
plt.tight_layout()
plt.show()


# Instantiate the class to load the data
# # data = Vinyard1WindRoseData()

# # Get the data
# wd, freq = data.get_data()

# # Plotting the wind rose
# fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': 'polar'})

# # Create a meshgrid for plotting
# ws_grid, wd_grid = np.meshgrid(ws, wd)

# # Convert wind direction to radians for polar plotting
# wd_rad = np.radians(wd_grid)

# # Plot the frequency as a pcolormesh plot
# c = ax.pcolormesh(wd_rad, ws_grid, freq, shading='auto', cmap='viridis')

# # Adding color bar
# fig.colorbar(c, ax=ax, label="Frequency [%]")

# # Set labels and title
# ax.set_xlabel('Wind Direction [°]')
# ax.set_ylabel('Wind Speed [m/s]')
# ax.set_title('Wind Rose - Frequency of Wind Speeds by Direction')

# # Show the plot
# plt.show()