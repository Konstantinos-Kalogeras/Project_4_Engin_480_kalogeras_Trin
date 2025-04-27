import numpy as np
import pandas as pd
import pywake
from py_wake.site._site import UniformWeibullSite
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_farm_models.engineering_models import PropagateDownwind
from pyproj import Transformer
import geopandas as gpd
import matplotlib.pyplot as plt

# Class for Turbine Positions
class VineyardWind_1:
    def __init__(self, geojson_path):
        self.geojson_path = geojson_path
        self.x = None
        self.y = None

    def convert_to_utm(self):
        gdf = gpd.read_file(self.geojson_path)
        gdf = gdf.to_crs(epsg=4326)

        # Extracting Point coordinates
        lon_list, lat_list = [], []
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

# Class to Handle Wind Rose Data (Wind Direction, Speed, Frequency)
class Vineyard1WindRoseData:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.wind_directions = None
        self.wind_speeds = None
        self.wind_frequencies = None
        self._load_data()

    def _load_data(self):
        df = pd.read_csv(self.csv_path)
        self.wind_directions = df['center_degrees'].to_numpy()
        self.wind_speeds = df['value'].to_numpy()
        self.wind_frequencies = df['value'].to_numpy()  # Assuming 'value' is frequency

    def get_data(self):
        return self.wind_directions, self.wind_speeds, self.wind_frequencies

# Class to Handle Wind Farm Boundary
class Vinyard_wind_boundarys:
    def __init__(self, geojson_path):
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

# Main AEP Simulation Class
class VineyardWindAEP:
    def __init__(self, turbine_capacity_mw=13, wind_data_path=None, turbine_positions_path=None, boundary_path=None):
        self.turbine_capacity_mw = turbine_capacity_mw
        self.wind_data_path = wind_data_path
        self.turbine_positions_path = turbine_positions_path
        self.boundary_path = boundary_path

        self.turbine_positions = None
        self.wind_directions = None
        self.wind_speeds = None
        self.wind_frequencies = None
        self.x = None
        self.y = None
        self.site = None
        self.wind_farm = None

        self._load_data()
        self._setup_site_and_farm()

    def _load_data(self):
        # Load turbine positions
        site = VineyardWind_1(self.turbine_positions_path)
        site.convert_to_utm()
        self.x, self.y = site.get_coordinates()

        # Load wind rose data
        wind_data = Vineyard1WindRoseData(self.wind_data_path)
        self.wind_directions, self.wind_speeds, self.wind_frequencies = wind_data.get_data()

    def _setup_site_and_farm(self):
        # Create a simple power curve
        wind_speeds_curve = np.arange(0, 26)  # 0 m/s to 25 m/s
        power_values = np.minimum((wind_speeds_curve/14)**3 * self.turbine_capacity_mw, self.turbine_capacity_mw)
        power_curve = np.array([wind_speeds_curve, power_values])

        turbine = WindTurbine(name='Turbine', diameter=120, hub_height=100, powerCtFunction=power_curve)

        # Define the wind farm model
        self.wind_farm = PropagateDownwind(site=None, windTurbines=turbine)

        # Define the site
        self.site = UniformWeibullSite(p_wd=[1/len(self.wind_directions)]*len(self.wind_directions),
                                       ti=0.1,  # Assume turbulence intensity
                                       ws_bins=self.wind_speeds)

    def run_aep_simulation(self):
        # Run the AEP simulation
        sim_res = self.wind_farm(x=self.x, y=self.y,
                                 wd=self.wind_directions,
                                 ws=self.wind_speeds)
        aep = sim_res.aep().sum()  # MWh
        print(f"AEP Simulation Result: {aep:.2f} MWh")
        return aep

    def plot_wind_farm(self):
        plt.figure(figsize=(10, 8))
        plt.scatter(self.x, self.y, color='green', label='Turbine Positions')

        # If boundary exists
        if self.boundary_path:
            boundary = Vinyard_wind_boundarys(self.boundary_path)
            boundary_x, boundary_y = zip(*boundary.get_utm())
            plt.plot(boundary_x, boundary_y, color='blue', label='Project Boundary')

        plt.title("Wind Farm Layout")
        plt.xlabel("Easting (m)")
        plt.ylabel("Northing (m)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

# Instantiate and Run
aep_simulator = VineyardWindAEP(
    wind_data_path="E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/windPowerRose.csv",
    turbine_positions_path="E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/posistions_of_Vinyard_wind_1_terbines.geojson",
    boundary_path="E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/outer_boundary_vinyard_wind_1.geojson"
)

# Run the AEP simulation
aep_result = aep_simulator.run_aep_simulation()

# Plot the wind farm layout
aep_simulator.plot_wind_farm()









################################### This file might help me but keeps running into erros ###########################################