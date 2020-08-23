author = "@rtphokie"
import unittest
from matplotlib import gridspec
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import requests
import requests_cache

requests_cache.install_cache('census_cache')

from pprint import pprint
import pandas as pd
import numpy as np

# https://api.census.gov/data/2020/dec/responserate.html
# https://www.census.gov/data/developers.html
# https://api.census.gov/data/2020/dec/responserate/variables.html
key="1686d53efc1d5b59c22bc7c54b7c755e88653a7a"

APIURLBASE='https://api.census.gov/data/2020/dec'


def get_response_by_county(county='*', state='37', tract='*',
                          PARAMSTOFETCH='GEO_ID,NAME,CRRALL,DRRALL,CRRINT,DRRINT,RESP_DATE'):
    return _get_response(county=county, state=state, tract=tract, datares='county',
                         PARAMSTOFETCH=PARAMSTOFETCH)

def get_response_by_tract(county='*', state='37', tract='*',
                          PARAMSTOFETCH='GEO_ID,NAME,CRRALL,DRRALL,CRRINT,DRRINT,RESP_DATE'):
    return _get_response(county=county, state=state, tract=tract, datares='tract',
                         PARAMSTOFETCH=PARAMSTOFETCH)

def _get_response(county='*', state='37', tract='*', datares='tract',
                  PARAMSTOFETCH='GEO_ID,NAME,CRRALL,DRRALL,CRRINT,DRRINT,RESP_DATE'):
    print(f"county {county}")
    url = f"{APIURLBASE}/responserate?get={PARAMSTOFETCH}&for={datares}:*&in=state:{state}&key={key}"
    print (url)
    r = requests.get(url)
    data = r.json()
    params = data[0]
    result = dict()
    for x in data[1:]:
        res = dict(zip(data[0], x))
        if 'tract' in res.keys():
            result[res['tract']] = res
        else:
            result[res['county']] = res
    return result


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

def _draw_data(ax, map, fig, colorbar=True, res="tract", state=37):
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
    data = get_response_by_tract(183)
    map.readshapefile(f'tl_2019_37_{res}/tl_2019_37_{res}', f'tl_2019_37_{res}', drawbounds=False)
    for info, shape in zip(map.tl_2019_37_tract_info, map.tl_2019_37_tract):
        if True or info['COUNTYFP'] == '183':

            try:
                census_response_record = data[info['TRACTCE']]
            except:
                census_response_record = None

            if census_response_record:
                color = cmap(norm(float(census_response_record['CRRALL'])))
                patches.append(Polygon(np.array(shape), True, color=color))
            else:
                nodata.append(info['TRACTCE'])
                pass
                # patches.append(Polygon(np.array(shape), True, color="grey"))
    pc = PatchCollection(patches, match_original=True, edgecolor='k', linewidths=.1, zorder=2)
    ax.add_collection(pc)

    if colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        # sm.set_array(colvals)
        fig.colorbar(sm, ax=ax, orientation="horizontal")

class MyTestCase(unittest.TestCase):

    def test_census_by_county(self):
        data = get_response_by_county()
        self.assertEqual(len(data), 100)

    def test_census_by_tract(self):
        data = get_response_by_tract()
        self.assertGreaterEqual(len(data), 1750)

    def test_NC_tracts(self):
        bounds = {'llcrnrlon': -84.6,
                  'llcrnrlat': 33.5,
                  'urcrnrlon': -75.2,
                  'urcrnrlat': 37.0,
                  'lon_0': -80.0,
                  }
        ax, fig, map = make_map(bounds)
        draw_tract_data(ax, map, fig)

        plt.show()




if __name__ == '__main__':
    unittest.main()
