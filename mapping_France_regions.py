import pandas as pd
import geopandas
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.feature import NaturalEarthFeature, COLORS
import numpy as np


# laod data from 2021
df = pd.read_excel('estimpop1.xls', sheet_name="2021", header=3) # from French government webpage
df_ = df[["Régions", "Unnamed: 6"]]
df_ = df_.drop(0)
df_ = df_.rename(columns={"Unnamed: 6": "2021"})

# rectify column name to ease mergin with geojson data
df_["Régions"][df_["Régions"] == "Martinique "] = "Martinique"
df_["Régions"][df_["Régions"] == "Guadeloupe "] = "Guadeloupe"
df_["Régions"][df_["Régions"] == "Centre-Val-de-Loire"] = "Centre-Val de Loire"


# read geojson data (regions limits as lat and long, got from french government)
reg = 'regions.geojson'
gdf = geopandas.read_file(reg)
gdf = gdf.drop([9, 11, 12, 10, 13])

# add columns per date to gdf
gdf['2021'] = 0
for reg in gdf["nom"]:
  gdf[str(2021)][gdf["nom"] == reg] = df_[str(2021)][df_["Régions"] == reg].values
  
  
# add column with all regions centroid to get latitude and longitude (to make a point on the map)
gdf.insert(loc = 3,
          column = 'centroid',
          value = gdf["geometry"].centroid)
gdf.insert(loc = 4,
          column = 'lat',
          value = gdf.centroid.map(lambda p: p.x))
gdf.insert(loc = 5,
          column = 'long',
          value = gdf.centroid.map(lambda p: p.y))

# function to build and display map on screen
def plot_me(col, title, cmap):
	# load map data
	resolution = "50m"
	BORDERS = NaturalEarthFeature('cultural', 'admin_0_boundary_lines_land',
                              resolution, edgecolor='black', facecolor='none')
	STATES = NaturalEarthFeature('cultural', 'admin_1_states_provinces_lakes',
                             resolution, edgecolor='black', facecolor='none')
	COASTLINE = NaturalEarthFeature('physical', 'coastline', resolution,
                                edgecolor='black', facecolor='none')
	LAKES = NaturalEarthFeature('physical', 'lakes', resolution,
                            edgecolor='face',
                            facecolor=COLORS['water'])
	LAND = NaturalEarthFeature('physical', 'land', resolution,
                           edgecolor='face',
                           facecolor=COLORS['land'], zorder=-1)
	OCEAN = NaturalEarthFeature('physical', 'ocean', resolution,
                            edgecolor='face',
                            facecolor=COLORS['water'], zorder=-1)
	RIVERS = NaturalEarthFeature('physical', 'rivers_lake_centerlines', resolution,
                             edgecolor=COLORS['water'],
                             facecolor='none')
	projection = ccrs.PlateCarree()
	fig = plt.figure(figsize=(8, 8))
	ax = fig.add_subplot(1, 1, 1, projection=projection)
	ax.add_feature(BORDERS)
	ax.add_feature(LAKES)
	ax.add_feature(LAND)
	ax.add_feature(OCEAN)
	ax.add_feature(RIVERS)
	ax.add_feature(COASTLINE)
	ax.set_extent([-5, 10, 41, 52])
	ax.set_title(title)
	# ax.gridlines(crs=projection, draw_labels=True,
 #             linewidth=2, color='gray', alpha=0.5, linestyle='--')

	gdf.plot(ax=ax, column=col, cmap=cmap, edgecolor='black', legend=True)
	# add countries names and numbers 
	for name in gdf["nom"]:
		plt.text(float(gdf["lat"][gdf["nom"] == name])-0.35, float(gdf["long"][gdf["nom"] == name]), "{}".format(name), size=6, color='darkgreen')
	plt.show()

plot_me('2021', "Population par région en 2021", "Reds")
