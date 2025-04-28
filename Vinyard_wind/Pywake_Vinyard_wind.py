# from Vinyard_Wind_1_quardinates_and_boundarys import Vinyard_wind_boundarys, VinyardWind_1
# import numpy as np
# import matplotlib.pyplot as plt
# from pywake import WindFarm
# # from py_wake.site import UniformSite
# # from py_wake.models import IAD  # Corrected import for IAD

# # Load turbine and boundary data
# site = VinyardWind_1()  # No need to pass the geojson path here, it's hardcoded in the class
# boundary = Vinyard_wind_boundarys()  # Same as above

# # Convert turbine positions to UTM
# site.convert_to_utm()
# turbine_x, turbine_y = site.get_coordinates()

# # Create the WindFarm with the turbines (UTM coordinates)
# turbines = np.column_stack((turbine_x, turbine_y))
# wind_farm = WindFarm(turbines)

# # Create a UniformSite for wind farm
# uniform_site = UniformSite(wind_farm)

# # Define wake model: IAD (Gaussian Wake model)
# wake_model = IAD()

# # Define wind conditions (wind speed and wind direction)
# wind_speed = 8  # Wind speed in m/s
# wind_direction = 270  # Wind direction in degrees (0 = North, 90 = East, 180 = South, 270 = West)

# # Simulate wake effects for each turbine
# results = wake_model(wind_farm, wind_direction, wind_speed)

# # Extract wake results (energy production, wake losses, etc.)
# energy_production = results['energy']
# wake_losses = results['wake_losses']  # This is the energy loss due to wake effects

# # Print the energy production results and wake losses
# print("Energy Production for each turbine:", energy_production)
# print("Wake Losses for each turbine:", wake_losses)

# # Plot the turbines and boundary
# boundary_x, boundary_y = zip(*boundary.get_utm())  # Extract boundary UTM coordinates

# plt.figure(figsize=(10, 8))

# # Plot turbine positions (green)
# plt.scatter(turbine_x, turbine_y, color='green', label='Turbine Positions')

# # Plot project boundary (red)
# plt.plot(boundary_x, boundary_y, color='red', label='Project Boundary')

# # Plot wake effects as circles around turbines (proportional to wake losses)
# for i, (x, y) in enumerate(zip(turbine_x, turbine_y)):
#     # Wake radius based on energy loss (or some other criteria)
#     # Example: simulate wake radius proportional to wake losses
#     wake_radius = np.sqrt(wake_losses[i])  # Wake radius in meters, proportional to loss
#     circle = plt.Circle((x, y), wake_radius, color='blue', alpha=0.3)  # Blue circles to represent wake areas
#     plt.gca().add_patch(circle)

# # Final plot settings
# plt.title('Vinyard Wind Farm Layout with Boundary and Wake Effects')
# plt.xlabel('Easting (m)')
# plt.ylabel('Northing (m)')
# plt.grid(True)
# plt.legend()
# plt.axis("equal")
# plt.tight_layout()
# plt.show()