import numpy as np
import geopandas as gpd
from pyproj import Transformer
import matplotlib.pyplot as plt
import pandas as pd


class Vinyard1WindRoseData:
    def __init__(self):
    
        self.csv_path = "E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\Vinyard_wind\windPowerRose.csv"
        
        # Data containers
        self.ws = None  # Wind speeds
        self.wd = None  # Wind directions
        self.freq = None  # Frequency matrix

        # Load data
        self._load_data()

    def _load_data(self):
    # Load CSV
        df = pd.read_csv(self.csv_path)

    # Strip any extra spaces in the column names
        df.columns = df.columns.str.strip()

    # Print column names to debug
        print("Columns in CSV:", df.columns)

    # Pivot the table (ensure the correct column names are used)
        wind_rose = df.pivot(index='Wind direction [°]',
                         columns='Wind speed [m/s]',
                         values='Frequency [%]').fillna(0)

    # Store data
        self.wd = wind_rose.index.to_numpy()
        self.ws = wind_rose.columns.to_numpy()
        self.freq = wind_rose.to_numpy()

    def get_data(self):
        """
        Returns a tuple: (wind_directions, wind_speeds, frequency_matrix)
        """
        return self.wd, self.ws, self.freq







# Class to handle the turbine positions
class VinyardWind_1:
    def __init__(self):
        # Hardcoded path to turbine positions GeoJSON
        geojson_path = "E:/Spring 2025/ENGIN 480/Porject_4/Project_4_Engin_480_kalogeras_Trin/Vinyard_wind/posistions_of_Vinyard_wind_1_terbines.geojson"
        self.geojson_path = geojson_path
        self.x = None
        self.y = None
        # How powerful the wind terbines are
        self.turbine_capacity_mw = 13e6

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


# Main execution
site = VinyardWind_1()
boundary = Vinyard_wind_boundarys()

site.convert_to_utm()
x, y = site.get_coordinates()
boundary_x, boundary_y = zip(*boundary.get_utm())

# Plotting
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
data = Vinyard1WindRoseData()

# Get the data
wd, ws, freq = data.get_data()

# Plotting the wind rose
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': 'polar'})

# Create a meshgrid for plotting
ws_grid, wd_grid = np.meshgrid(ws, wd)

# Convert wind direction to radians for polar plotting
wd_rad = np.radians(wd_grid)

# Plot the frequency as a pcolormesh plot
c = ax.pcolormesh(wd_rad, ws_grid, freq, shading='auto', cmap='viridis')

# Adding color bar
fig.colorbar(c, ax=ax, label="Frequency [%]")

# Set labels and title
ax.set_xlabel('Wind Direction [°]')
ax.set_ylabel('Wind Speed [m/s]')
ax.set_title('Wind Rose - Frequency of Wind Speeds by Direction')

# Show the plot
plt.show()