import pandas as pd
import requests


def get_snb_data():
    data = pd.read_csv('https://data.snb.ch/api/cube/snbbipo/data/csv/de', header=2, delimiter=';')
    return data

data = get_snb_data()

def get_snb_dimensions():
    url = 'https://data.snb.ch/api/cube/snbbipo/dimensions/de'
    data_dimensions = requests.get(url).json()
    data_dimensions = data_dimensions['dimensions']
    dimensions = pd.json_normalize(data_dimensions,
        record_path=['dimensionItems', 'dimensionItems'], 
        meta=[
            'name',
            ['dimensionItems','name']
            ],
        meta_prefix='meta_'
    )
    dimensions.drop(columns=['meta_name'], inplace=True)
    dimensions.rename(columns={"id": "position_id", "name": "position_name", "meta_dimensionItems.name": "position_category"}, inplace=True)
    return dimensions

dimensions = get_snb_dimensions()

moneyness = {"position_id":{"0":"GFG","1":"D","2":"RIWF","3":"IZ","4":"W","5":"FRGSF","6":"FRGUSD","7":"GSGSF","8":"IG",
"9":"GD","10":"FI","11":"WSF","12":"DS","13":"UA","14":"T0","15":"N","16":"GB","17":"VB","18":"GBI",
"19":"US","20":"VRGSF","21":"ES","22":"UT","23":"VF","24":"AIWFS","25":"SP","26":"RE","27":"T1"}, 
"moneyness":{"0":"Else","1":"CHF","2":"Else","3":"Else","4":"Else","5":"CHF","6":"Else","7":"CHF","8":"CHF",
"9":"CHF","10":"CHF","11":"CHF","12":"CHF","13":"CHF","14":"Else","15":"CHF","16":"CHF","17":"CHF","18":"CHF",
"19":"CHF","20":"CHF","21":"CHF","22":"CHF","23":"Else","24":"Else","25":"Else","26":"Else","27":"Else"}}

moneyness = pd.DataFrame.from_dict(moneyness)
dimensions = pd.merge(dimensions, moneyness, how='left',left_on='position_id',right_on='position_id', copy=False)
data =  pd.merge(data,dimensions, how='left',left_on='D0',right_on='position_id', copy=False).drop('D0', axis=1)

print(data.head(30))