import numpy as np
import geopandas as gpd
from pyproj import Transformer
import matplotlib.pyplot as plt
import pandas as pd

class VineyardWindProject:
    def __init__(self, wind_data_path, geojson_path, boundary_path):
        # Wind data CSV path
        self.wind_data_path = wind_data_path
        
        # GeoJSON paths for turbines and boundary
        self.geojson_path = geojson_path
        self.boundary_path = boundary_path
        
        # Data variables
        self.wd = None  # Wind directions
        self.freq = None  # Frequencies
        self.x = None  # UTM X coordinates for turbines
        self.y = None  # UTM Y coordinates for turbines
        self.boundary_x = None  # Boundary UTM X coordinates
        self.boundary_y = None  # Boundary UTM Y coordinates
        
        self._load_data()
        self._load_turbine_positions()
        self._load_boundary()

    def _load_data(self):
        """
        Loads the wind rose data from a CSV file
        """
        df = pd.read_csv(self.wind_data_path)
        print("Columns in Wind Data CSV:", df.columns)

        self.wd = df['center_degrees'].to_numpy()
        self.freq = df['value'].to_numpy()

    def _load_turbine_positions(self):
        """
        Loads the turbine position data from the GeoJSON file and converts to UTM coordinates.
        """
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

    def _load_boundary(self):
        """
        Loads the project boundary data from the GeoJSON and converts to UTM coordinates.
        """
        gdf = gpd.read_file(self.boundary_path)

        if gdf.crs is None:
            gdf.set_crs(epsg=4326, inplace=True)

        self.boundary_latlon = np.array(gdf.geometry.iloc[0].coords)
        utm_crs = self._get_utm_crs(gdf)
        self.gdf_utm = gdf.to_crs(utm_crs)
        self.boundary_utm = np.array(self.gdf_utm.geometry.iloc[0].coords)

        self.boundary_x, self.boundary_y = zip(*self.boundary_utm)

    def _get_utm_crs(self, gdf):
        """
        Calculate the appropriate UTM zone for the project boundary.
        """
        centroid = gdf.geometry.centroid.iloc[0]
        lon = centroid.x
        utm_zone = int((lon + 180) / 6) + 1
        return f"EPSG:{32600 + utm_zone}"

    def plot_turbines_and_boundary(self):
        """
        Plot the turbine positions and project boundary in UTM coordinates.
        """
        plt.figure(figsize=(10, 8))
        plt.scatter(self.x, self.y, color='green', label='Turbine Positions')
        plt.plot(self.boundary_x, self.boundary_y, color='blue', label='Project Boundary')
        plt.title("Vineyard Wind 1 - UTM Coordinates")
        plt.xlabel("Easting (m)")
        plt.ylabel("Northing (m)")
        plt.grid(True)
        plt.legend()
        plt.axis("equal")
        plt.tight_layout()
        plt.show()

    def plot_wind_rose(self):
        """
        Plot the wind rose using the wind rose data.
        """
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': 'polar'})

        # Convert wind direction to radians for polar plotting
        wd_rad = np.radians(self.wd)

        # Plotting the wind rose (frequency vs direction)
        c = ax.bar(wd_rad, self.freq, width=0.3, color='blue', alpha=0.6)

        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_title('Wind Rose - Frequency of Wind Speeds by Direction')

        plt.show()

# Main execution
if __name__ == "__main__":
    # Set paths
    wind_data_path = "E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/windPowerRose.csv"
    geojson_path = "E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/posistions_of_Vinyard_wind_1_terbines.geojson"
    boundary_path = "E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/outer_boundary_vinyard_wind_1.geojson"

    # Create an instance of the project class
    vineyard_project = VineyardWindProject(wind_data_path, geojson_path, boundary_path)

    # Plot turbines and boundary
    vineyard_project.plot_turbines_and_boundary()

    # Plot the wind rose
    vineyard_project.plot_wind_rose()