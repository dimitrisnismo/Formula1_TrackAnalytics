
__version__ = '2.1.13'
base_url = 'http://ergast.com/api/f1'
_headers = {'User-Agent': f'FastF1/{__version__}'}

year=2021
gp=5

import requests
url = f"{base_url}/{year}/{gp}.json"
data = requests.get(url, headers=_headers)


url = ("https://www.mapcoordinates.net/admin/component/edit/"
        + "Vpc_MapCoordinates_Advanced_GoogleMapCoords_Component/"
        + "Component/json-get-elevation")
loc = data['Circuit']['Location']
body = {'longitude': loc['long'], 'latitude': loc['lat']}


res = _parse_json_response(requests.post(url, data=body))

data['Circuit']['Location']['alt'] = 1
