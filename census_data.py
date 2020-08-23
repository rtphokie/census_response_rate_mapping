import requests

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
