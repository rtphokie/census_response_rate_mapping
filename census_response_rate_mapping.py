author = "@rtphokie"
# https://api.census.gov/data/2020/dec/responserate.html
# https://www.census.gov/data/developers.html
# https://api.census.gov/data/2020/dec/responserate/variables.html
# https://www2.census.gov/geo/maps/DC2020/SR20/ shapefiles
# https://public.tableau.com/views/ResponseRateChallenge/CountyDashboard?:showVizHome=no&:tabs=n&State=North%20Carolina&Select%20Mode=Total&Share
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from pprint import pprint
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from census_data import get_response_by_tract, get_response_by_county
import pandas as pd
import numpy as np


def make_map(bounds, projection='mill', resolution='i'):
    '''
    :param bounds: dictionary with lat/lon bounds for lower left and upper right
    :param projection: defaults to mill (Miller Cylindrical Projection) used in NWS/NHC/NOAA maps
    :return:
    '''
    fig = plt.figure(num=None, figsize=(16, 9), dpi=300, facecolor='w', edgecolor='w')
    ax = fig.add_subplot(111)
    ax.axis('off') # lat/lon axis not needed on plotted map

    map = Basemap(projection=projection,
                  resolution=resolution,
                  lon_0=bounds['lon_0'],
                  llcrnrlon=bounds['llcrnrlon'],
                  llcrnrlat=bounds['llcrnrlat'],
                  urcrnrlon=bounds['urcrnrlon'],
                  urcrnrlat=bounds['urcrnrlat'])
    map.drawmapboundary(fill_color='black')
    map.drawcounties(linewidth=1.2, linestyle='solid', color='black',zorder=9)
    map.fillcontinents(color='white', lake_color='white')

    return ax, fig, map

def draw_tract_data(ax, map, fig, state=37, colorbar=True, counties=[]):
    # wrapper for _draw_data
    return _draw_data(ax, map, fig, colorbar=True, res="tract", state=state, counties=counties)

def draw_county_data(ax, map, fig, state=37, colorbar=True, counties=[]):
    # wrapper for _draw_data
    return _draw_data(ax, map, fig, colorbar=True, res="county", state=state, counties=counties)

def _draw_data(ax, map, fig, colorbar=True, res="tract", state=37, year=2019, counties=[]):
    '''
    # shapefile source: https://www2.census.gov/geo/maps/DC2020/SR20/
    # Note: ESRI shapefiles from the Census are sometimes ready to go, sometimes require conversion from verticies to
    #       coordinate base polygons (brew install gdal for mac users):
    #       %  ogr2ogr -t_srs EPSG:4326 tract_bas20_sr_500k_coordinates.shp tract_bas20_sr_500k.shp
    #       It can be reduced to just the state of interest, strongly recommended for performance
    #       % ogr2ogr -t_srs EPSG:4326-sql "select * from tract_bas20_sr_500k where STATE='37'" tract_bas20_sr_500k_37.shp tract_bas20_sr_500k.shp
    :param ax: matplotlib axis to use
    :param map: Basemap previously by make_map
    :return: nothing

    Note: the
    '''
    patches = []
    nodata = []
    vals = []
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(0, 100)


    # build list of zero padded 3 digit strings
    countiesstr=[]
    for county in counties:
        countiesstr.append(f"{county:03}")

    # using US Census Bureau filename pattern
    shpdir = f"data/sr20_500k"
    if res == 'tract':
        data = get_response_by_tract()
        datakey = res.upper()
        shpfilename = f"tract_bas20_sr_500k_{state}"
    elif res == 'county':
        data = get_response_by_county()
        datakey = res.upper()
        shpfilename = f"county_bas20_sr_500k_{state}"
    else:
        raise ValueError(f"unknown geo resolution {res}, expected county or tract")

    map.readshapefile(f'{shpdir}/{shpfilename}', shpfilename, drawbounds=False)

    shpinfoobj = shpobj = None
    for param in map.__dict__.keys():  # gross but enables function reuse
        if param == shpfilename:
            shpinfoobj = map.__dict__[f"{shpfilename}_info"]
            shpobj = map.__dict__[shpfilename]
    if shpobj is None:
        raise ValueError(f'shape object not found in map object, check shapefiles in {shpfilename}')

    rates = []
    for info, shape in zip(shpinfoobj, shpobj):
        if info['STATE'] != str(state):
            continue
        if info[datakey] in data.keys():
            if len(counties) == 0 or info['COUNTY'] in countiesstr:
                if float(data[info[datakey]]['CRRALL']) < 5.0:
                    # as of Aug 21, all sub 5% returns are from uninhabited areas (nat forests, Ft. Bragg training areas, commercially zoned areas of RTP)
                    continue
                else:
                    rates.append(float(data[info[datakey]]['CRRALL']))
        else:
            print(f"not data for {info['COUNTY']} {info['TRACT']}")
    norm = plt.Normalize(min(rates), 100)


    for info, shape in zip(shpinfoobj, shpobj):
        if info['STATE'] != str(state):
            continue
        try:
            if info[datakey] in data.keys():
                if len(counties) == 0 or info['COUNTY'] in countiesstr:
                    if float(data[info[datakey]]['CRRALL']) < 10.0:
                        # as of Aug 21, all sub 10% returns are from uninhabited areas (nat forests, Ft. Bragg training areas, commercially zoned areas of RTP)
                        continue
                    color = cmap(norm(float(data[info[datakey]]['CRRALL'])))
                    patches.append(Polygon(np.array(shape), True, color=color))
            else:
                nodata.append(info[datakey])
        except:
            pprint(info)
            print('failed')
            raise

    # pc = PatchCollection(patches, match_original=True, edgecolor='grey', linewidths=.05, zorder=2)
    pc = PatchCollection(patches, match_original=True, zorder=2)
    ax.add_collection(pc)

    if colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        # sm.set_array(colvals)
        fig.colorbar(sm, ax=ax, orientation="horizontal")
    return data
