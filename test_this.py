author = "@rtphokie"
import unittest
import matplotlib.pyplot as plt
from pprint import pprint
import requests_cache
import pandas as pd
from census_response_rate_mapping import make_map, draw_tract_data, draw_county_data
from census_data import get_response_by_county, get_response_by_tract, get_bounding_box, get_dma_data
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class MyTestCase(unittest.TestCase):
    def test_get_bounding_box_data(self):
        df, data = get_bounding_box()
        self.assertEqual(len(df), 3221)
        df, data = get_bounding_box(state=37)
        self.assertEqual(len(df), 100)
        df, data = get_bounding_box(state=37, counties=[183, 63])
        self.assertEqual(len(df), 2)

    def test_map_wake_by_tract(self):
        # Counties in Raleigh-Durham DMA
        # df, countyfips = get_dma_data('RALEIGH (NC) - DURHAM (NC) - FAYETTEVILLE (NC)', state="NC")
        countyfips=[183]
        df, bounds = get_bounding_box(state=37, counties=countyfips)
        ax, fig, map = make_map(bounds)
        draw_tract_data(ax, map, fig, counties=countyfips)
        plt.show()
        fig.savefig('census_NC_tracts.png')

    def test_get_DMA_data(self):
        data, countyfips = get_dma_data('RALEIGH (NC) - DURHAM (NC) - FAYETTEVILLE (NC)', state="NC")
        self.assertEqual(21, len(data))

    def test_map_central_NC_tracts(self):
        #Counties in Raleigh-Durham DMA
        df, countyfips = get_dma_data('RALEIGH (NC) - DURHAM (NC) - FAYETTEVILLE (NC)', state="NC")
        df_geo, bounds = get_bounding_box(state=37, counties=countyfips)
        ax, fig, map = make_map(bounds)
        data = draw_tract_data(ax, map, fig, counties=countyfips)
        df_response = pd.DataFrame.from_dict(data, orient='index')
        atoms=[]
        for county in countyfips:
            atoms.append(f'county == "{county:03}"')
        df_response.query(" or ".join(atoms), inplace = True)
        df_response.to_excel("central_nc_tracts.xlsx")
        plt.show()
        fig.savefig('census_central_NC_tracts.png')

    def test_map_NC_counties(self):
        df, bounds = get_bounding_box(state=37)
        ax, fig, map = make_map(bounds)
        data = draw_county_data(ax, map, fig)
        df_response = pd.DataFrame.from_dict(data, orient='index')
        df_response.to_excel("nc_counties.xlsx")
        print(df_response)
        plt.show()
        fig.savefig('census_NC_counties.png')

if __name__ == '__main__':
    unittest.main()
