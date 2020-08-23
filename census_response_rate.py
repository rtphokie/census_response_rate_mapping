author = "@rtphokie"
# https://api.census.gov/data/2020/dec/responserate.html
# https://www.census.gov/data/developers.html
# https://api.census.gov/data/2020/dec/responserate/variables.html

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from census_data import get_response_by_tract, get_response_by_county

import numpy as np


def make_map(bounds, projection='mill', resolution='i'):
    '''
    :param bounds: dictionary with lat/lon bounds for lower left and upper right
    :param projection: defaults to mill (Miller Cylindrical Projection) used in NWS/NHC/NOAA maps
    :return:
    '''
    fig = plt.figure(num=None, figsize=(16, 9), dpi=300, facecolor='w', edgecolor='w')
    ax = fig.add_subplot(111)
    map = Basemap(projection=projection,
                  resolution=resolution,
                  lon_0=bounds['lon_0'],
                  llcrnrlon=bounds['llcrnrlon'],
                  llcrnrlat=bounds['llcrnrlat'],
                  urcrnrlon=bounds['urcrnrlon'],
                  urcrnrlat=bounds['urcrnrlat'])
    map.drawmapboundary(fill_color='white')
    map.fillcontinents(color='white', lake_color='white')

    return ax, fig, map

def draw_tract_data(ax, map, fig, state=37, colorbar=True):
    # wrapper for _draw_data
    return _draw_data(ax, map, fig, colorbar=True, res="tract", state=state)

def draw_county_data(ax, map, fig, state=37, colorbar=True):
    # wrapper for _draw_data
    return _draw_data(ax, map, fig, colorbar=True, res="county", state=state)

def _draw_data(ax, map, fig, colorbar=True, res="tract", state=37, year=2019):
    '''
    # shapefile source: https://www2.census.gov/geo/tiger/TIGER2019/COUNTY/
    :param ax: matplotlib axis to use
    :param map: Basemap previously by make_map
    :return: nothing
    '''
    patches = []
    nodata = []
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(0, 100)
    data = get_response_by_tract()

    if res == 'tract':
        shp=f"tl_{year}_{state}_{res}"
    elif res == 'tract':
        shp = f"tl_{year}_us_county"
    else:
        raise ValueError(f"unknown geo resolution {res}, expected county or tract")

    map.readshapefile(f'{shp}/{shp}', shp, drawbounds=False)
    # from pprint import pprint
    # pprint(map.__dict__.keys())
    # raise
    for info, shape in zip(map.tl_2019_37_tract_info, map.tl_2019_37_tract):
        if True or info['COUNTYFP'] == '183':

            if info['TRACTCE'] in data.keys():
                census_response_record = data[info['TRACTCE']]
                color = cmap(norm(float(data[info['TRACTCE']]['CRRALL'])))
                patches.append(Polygon(np.array(shape), True, color=color))
            else:
                nodata.append(info['TRACTCE'])

    pc = PatchCollection(patches, match_original=True, edgecolor='k', linewidths=.1, zorder=2)
    ax.add_collection(pc)

    if colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        # sm.set_array(colvals)
        fig.colorbar(sm, ax=ax, orientation="horizontal")