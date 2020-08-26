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

requests_cache.install_cache('census_cache')


class MyTestCase(unittest.TestCase):

    def test_get_bounding_box_data(self):
        df, data = get_bounding_box()
        self.assertEqual(len(df), 3221)
        df, data = get_bounding_box(state=37)
        self.assertEqual(len(df), 100)
        df, data = get_bounding_box(state=37, counties=[183, 63])
        self.assertEqual(len(df), 2)

    def test_census_by_county(self):
        data = get_response_by_county()
        self.assertEqual(len(data), 100)

    def test_census_by_tract(self):
        data = get_response_by_tract()
        self.assertGreaterEqual(len(data), 1750)

    def test_map_wake_by_tract(self):
        # Counties in Raleigh-Durham DMA
        # df, countyfips = get_dma_data('RALEIGH (NC) - DURHAM (NC) - FAYETTEVILLE (NC)', state="NC")
        countyfips=[183]
        df, bounds = get_bounding_box(state=37, counties=countyfips)
        ax, fig, map = make_map(bounds)
        draw_tract_data(ax, map, fig, counties=countyfips)
        plt.show()
        fig.savefig('census_NC_tracts.png')

    def test_map_central_NC_tracts(self):
        #Counties in Raleigh-Durham DMA
        df, countyfips = get_dma_data('RALEIGH (NC) - DURHAM (NC) - FAYETTEVILLE (NC)', state="NC")
        df, bounds = get_bounding_box(state=37, counties=countyfips)
        ax, fig, map = make_map(bounds)
        draw_tract_data(ax, map, fig, counties=countyfips)
        plt.show()
        fig.savefig('census_NC_tracts.png')

    def test_get_DMA_data(self):
        data, countyfips = get_dma_data('RALEIGH (NC) - DURHAM (NC) - FAYETTEVILLE (NC)', state="NC")
        self.assertEqual(21, len(data))


    def test_map_NC_tracts(self):
        df, bounds = get_bounding_box(state=37)

        ax, fig, map = make_map(bounds)
        data = draw_tract_data(ax, map, fig)
        df = pd.DataFrame(data.values())
        df.to_excel("NC_tracts.xlsx")

        plt.show()
        fig.savefig('census_NC_tracts.png')

    def test_map_NC_counties(self):
        df, bounds = get_bounding_box(state=37)

        ax, fig, map = make_map(bounds)
        draw_county_data(ax, map, fig)
        plt.show()
        fig.savefig('census_NC_counties.png')

    def test_map_central_NC_counties(self):
        countylist=[183,63, 37, 51, 65, 69, 77, 83, 85, 93, 101, 105, 127, 131, 135, 145, 163, 181, 185, 191, 195]
        df, bounds = get_bounding_box(state=37, counties=countylist)
        ax, fig, map = make_map(bounds)
        draw_tract_data(ax, map, fig, counties=countylist)
        plt.show()
        fig.savefig('census_NC_tracts.png')

    def test_filter(self):
        from osgeo import ogr
        import os

        inShapefile = "sr20_500k/tract_bas20_sr_500k.shp"
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(inShapefile, 0)
        inLayer = inDataSource.GetLayer()

        # Create the output Layer
        outShapefile = "states_centroids.shp"
        outDriver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        outLayer = outDataSource.CreateLayer("states_centroids", geom_type=ogr.wkbPoint)

        # Add input Layer Fields to the output Layer
        inLayerDefn = inLayer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)

        # Get the output Layer's Feature Definition
        outLayerDefn = outLayer.GetLayerDefn()

        # Add features to the ouput Layer
        for i in range(0, inLayer.GetFeatureCount()):
            # Get the input Feature
            inFeature = inLayer.GetFeature(i)
            # Create output Feature
            outFeature = ogr.Feature(outLayerDefn)
            # Add field values from input Layer
            for i in range(0, outLayerDefn.GetFieldCount()):
                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
            # Set geometry as centroid
            geom = inFeature.GetGeometryRef()
            inFeature = None
            centroid = geom.Centroid()
            outFeature.SetGeometry(centroid)
            # Add new feature to output Layer
            outLayer.CreateFeature(outFeature)
            outFeature = None

        # Save and close DataSources
        inDataSource = None
        outDataSource = None
    unittest.main()


