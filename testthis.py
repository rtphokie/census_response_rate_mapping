author = "@rtphokie"
import unittest
import matplotlib.pyplot as plt
import requests_cache
from census_response_rate import make_map, draw_tract_data, draw_county_data
from census_data import get_response_by_county, get_response_by_tract


requests_cache.install_cache('census_cache')


class MyTestCase(unittest.TestCase):

    def test_census_by_county(self):
        data = get_response_by_county()
        self.assertEqual(len(data), 100)

    def test_census_by_tract(self):
        data = get_response_by_tract()
        self.assertGreaterEqual(len(data), 1750)

    def test_NC_tracts(self):
        bounds = {'llcrnrlon': -84.6, 'llcrnrlat': 33.5,
                  'urcrnrlon': -75.2, 'urcrnrlat': 37.0,
                  'lon_0': -80.0,
                  }
        ax, fig, map = make_map(bounds)
        draw_tract_data(ax, map, fig)
        plt.show()

    def test_NC_counties(self):
        bounds = {'llcrnrlon': -84.6, 'llcrnrlat': 33.5,
                  'urcrnrlon': -75.2, 'urcrnrlat': 37.0,
                  'lon_0': -80.0,
                  }
        ax, fig, map = make_map(bounds)
        draw_county_data(ax, map, fig)
        plt.show()

if __name__ == '__main__':
    unittest.main()
