import requests
from os import path
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

key="1686d53efc1d5b59c22bc7c54b7c755e88653a7a"
APIURLBASE='https://api.census.gov/data/2020/dec'

def get_response_by_county(county='*', state='37', tract='*',
                          PARAMSTOFETCH='GEO_ID,NAME,CRRALL,CRRINT,RESP_DATE'):
    return _get_response(county=county, state=state, tract=tract, datares='county',
                         PARAMSTOFETCH=PARAMSTOFETCH)

def get_response_by_tract(county='*', state='37', tract='*',
                          PARAMSTOFETCH='GEO_ID,NAME,CRRALL,CRRINT,RESP_DATE'):
    return _get_response(county=county, state=state, tract=tract, datares='tract',
                         PARAMSTOFETCH=PARAMSTOFETCH)

def _get_response(county='*', state='37', tract='*', datares='tract',
                  PARAMSTOFETCH='GEO_ID,NAME,CRRALL,CRRINT,RESP_DATE'):
    url = f"{APIURLBASE}/responserate?get={PARAMSTOFETCH}&for={datares}:*&in=state:{state}&key={key}"
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


def get_bounding_box(state=None, counties=[]):
    '''
    
    :param state: optional state FIPS code to filter by (e.g. NC=37)
    :param counties: optional list of county FIPS codes to filter by (e.g. NC Wake = 183)
    :return: 
    '''
    filename = 'bounding.csv'
    if not path.exists(filename):
        url = 'https://raw.githubusercontent.com/stucka/us-county-bounding-boxes/master/bounding.csv'
        r = requests.get(url, allow_redirects=True)
        open(filename, 'wb').write(r.content)

    df = pd.read_csv(filename)
    if state is not None:
        df.query('statefips == 37', inplace=True)
    if counties:
        atoms = []
        for county in counties:
            atoms.append(f"countyfips == {county}")
        df.query(" or ".join(atoms), inplace = True)

    bounds = {'llcrnrlon': df['extentw'].min(), 'llcrnrlat': df['extents'].min(),
              'urcrnrlon':df['extente'].max(), 'urcrnrlat': df['extentn'].max(),
              'lon_0': np.mean([df['extentw'].min(),df['extente'].min()])
              }
    return df, bounds