#%%
"""
東京都の行政区域のデータ(geojson形式)を読み込んで、指定した都市市の行政区域のデータのみ取り出して
ファイル(geojson形式)にして出力
- 入力ファイルの仕様
　国土数値情報　行政区域データ
　http://nlftp.mlit.go.jp/ksj/jpgis/datalist/KsjTmplt-N03.html
"""

#%%
# モジュールインポート
import json
import numpy as np
from shapely.geometry import Point, Polygon
from IPython.core.display import display        


# -------------------------------------------------------------------------------
# N03(行政区域関連)の関数
# -------------------------------------------------------------------------------

def district_henkan(source_filepath, target_filepath, prefecture_name, city_name):
    # geojsonファイルを読み込む
    with open(source_filepath, 'r') as f:
        district_geojson_all = json.load(f)

    # geojson形式のfeaturesのリストから指定した都市に該当するもののみ取り出す
    district_geojson_target={}
    district_geojson_target['type']='FeatureCollection'
    district_geojson_target['features'] = []

    for geojson_feature in district_geojson_all['features']:
        prop = geojson_feature['properties']
        if (prop['N03_001'] == prefecture_name and prop['N03_004'] == city_name):
            district_geojson_target['features'].append(geojson_feature)

    # geojson形式のファイルに出力
    with open(target_filepath, 'w') as f:
        json.dump(district_geojson_target, f, ensure_ascii=False, indent=4)
    
    # 戻り値
    return district_geojson_target



# -------------------------------------------------------------------------------
# A27(小学校関連)の関数
# -------------------------------------------------------------------------------
def elementaryLoc_henkan(source_loc_filepath, target_loc_filepath, city_name):
    # geojsonファイルを読み込む
    with open(source_loc_filepath, 'r') as f:
        elementary_loc_all = json.load(f)

    # featuresのリストから指定した都市に該当するもののみ取り出す
    elementary_loc_target={}
    elementary_loc_target['type']='FeatureCollection'
    elementary_loc_target['features'] = []

    for geojson_feature in elementary_loc_all['features']:
        prop = geojson_feature['properties']
        if (city_name in prop['A27_004']): # A27_004は住所
            elementary_loc_target['features'].append(geojson_feature)


    # 小学校位置:Elementary_loc.geojson(パパマママップ)のデータ仕様合わせて形式変更
    for item in elementary_loc_target['features']:
        prop = item['properties']

        # 項目名の変更
        prop['A27_005'] = prop.pop('A27_001') # A27_001 -> A27_005
        prop['A27_006'] = prop.pop('A27_002') # A27_002 -> A27_006
        prop['A27_007'] = prop.pop('A27_003') # A27_003 -> A27_007
        prop['A27_008'] = prop.pop('A27_004') # A27_004 -> A27_008

        # labelの追加
        prop['label'] = prop['A27_007']

        # x,y座標の追加
        x, y = item['geometry']['coordinates']
        prop['x'] = x
        prop['y'] = y

    # geojsonファイル(ELementary_loc.geojson)に出力
    with open(target_loc_filepath, 'w') as f:
        json.dump(elementary_loc_target, f, ensure_ascii=False, indent=4)

    # 戻り値
    return elementary_loc_target


def elementaryPoly_henkan(source_poly_filepath, target_poly_filepath, target_loc_filepath, city_name):
    # ------------------------------------------------------------------
    # 小学校のポリゴンデータから指定した都市のデータを取り出す
    # ------------------------------------------------------------------
    # A27-16_13.geojson
    # geojsonファイルをdictionary型でload
    with open(source_poly_filepath, 'r') as f:
        elementary_poly_all = json.load(f)

    with open(target_loc_filepath, 'r') as f:
        elementary_loc_target = json.load(f)
    

    # featuresのリストから指定した都市に該当するもののみ取り出す
    elementary_poly_target={}
    elementary_poly_target['type']='FeatureCollection'
    elementary_poly_target['features'] = []
    
    for geojson_feature in elementary_poly_all['features']:
        prop = geojson_feature['properties']
        if (city_name in prop['A27_008']): # A27_008は住所
            elementary_poly_target['features'].append(geojson_feature)

    # 小学校ポリゴン:Elementary.geojson(パパマママップ)用に形式を変更
    # A27_007 -> name 
    # A27_008 -> address
    for item in elementary_poly_target['features']:
        prop = item['properties']

        # フィールド名の変更
        prop['name'] = prop.pop('A27_007')
        prop['address'] = prop.pop('A27_008')

        # Elementary_locを用いて小学校名からx,yを算出
        x = 0.0
        y = 0.0
        name = prop['name']
        for elem in elementary_loc_target['features']:
            if elem['properties']['A27_007'] == name:
                x = elem['properties']['x']
                y = elem['properties']['y']

        if (x != 0.0) and (y != 0.0):
            prop['x'] = x
            prop['y'] = y
        else:
            print(name, ":位置情報を取得できませんでした")

    # geojsonファイル(ELementary.geojson)に出力
    with open(target_poly_filepath, 'w') as f:
        json.dump(elementary_poly_target, f, ensure_ascii=False, indent=4)

    # 返り値
    return elementary_poly_target


# -------------------------------------------------------------------------------
# A32(中学校関連)の関数
# -------------------------------------------------------------------------------
def middleschoolLoc_henkan(source_loc_filepath, target_loc_filepath, city_name):
    # geojsonファイルを読み込む
    with open(source_loc_filepath, 'r') as f:
        middleschool_loc_all = json.load(f)

    # featuresのリストから指定した都市に該当するもののみ取り出す
    middleschool_loc_target={}
    middleschool_loc_target['type']='FeatureCollection'
    middleschool_loc_target['features'] = []

    for geojson_feature in middleschool_loc_all['features']:
        prop = geojson_feature['properties']
        if (city_name in prop['A32_004']):
            middleschool_loc_target['features'].append(geojson_feature)

    # 中学校位置:middleschool_loc.geojson(パパマママップ)のデータ仕様合わせて形式変更
    for item in middleschool_loc_target['features']:
        prop = item['properties']

        # 項目名の変更
        prop['address'] = prop.pop('A32_004') # A32_004 -> address

        # labelの追加
        prop['label'] = prop['A32_003']

        # x,y座標の追加
        x, y = item['geometry']['coordinates']
        prop['x'] = x
        prop['y'] = y

        # 項目の削除
        prop.pop('A32_005')

    # geojsonファイル(Middleschool_loc.geojson)に出力
    with open(target_loc_filepath, 'w') as f:
        json.dump(middleschool_loc_target, f, ensure_ascii=False, indent=4)

    # 戻り値
    return middleschool_loc_target


def middleschoolPoly_henkan(source_poly_filepath, target_poly_filepath, target_loc_filepath, city_name):
    # ------------------------------------------------------------------
    # 中学校のポリゴンデータから指定した都市市のデータを取り出す
    # ------------------------------------------------------------------
    # geojsonファイルをdictionary型でload
    with open(source_poly_filepath, 'r') as f:
        middleschool_poly_all = json.load(f)

    with open(target_loc_filepath, 'r') as f:
        middleschool_loc_target = json.load(f)
    
    # featuresのリストから指定した都市に該当するもののみ取り出す
    middleschool_poly_target={}
    middleschool_poly_target['type']='FeatureCollection'
    middleschool_poly_target['features'] = []
    
    for geojson_feature in middleschool_poly_all['features']:
        prop = geojson_feature['properties']
        if (city_name in prop['A32_009']):
            middleschool_poly_target['features'].append(geojson_feature)

    # 中学校ポリゴン:Elementary.geojson(パパマママップ)用に形式を変更
    for item in middleschool_poly_target['features']:
        prop = item['properties']

        # フィールド名の変更
        prop['name'] = prop.pop('A32_008')
        prop['address'] = prop.pop('A32_009')

        # Elementary_locを用いて小学校名からx,yを算出
        x = 0.0
        y = 0.0
        name = prop['name']
        for elem in middleschool_loc_target['features']:
            if elem['properties']['A32_003'] == name:
                x = elem['properties']['x']
                y = elem['properties']['y']

        if (x != 0.0) and (y != 0.0):
            prop['x'] = x
            prop['y'] = y
        else:
            print(name, ":位置情報を取得できませんでした")

        # フィールドの削除
        prop.pop('A32_007')
        prop.pop('A32_010')

    # geojsonファイルに出力
    with open(target_poly_filepath, 'w') as f:
        json.dump(middleschool_poly_target, f, ensure_ascii=False, indent=4)

    # 返り値
    return middleschool_poly_target


# -------------------------------------------------------------------------------
# N02(鉄道関連)の関数
# -------------------------------------------------------------------------------

def avg_point(point_list):
    # 複数の点の座標の中心を求める
    sum_point = np.array([0.0, 0.0])
    for point in point_list:
        sum_point = sum_point + np.array(point)
    
    return (sum_point/len(point_list)).tolist()


def point_within_polygon(point_coord, polygon_coord):
    '''
    point_coord : eg. (0.5,0.5)
    return : True if point is within area_polygon, else False
    '''
    p = Point(point_coord)
    poly = Polygon(polygon_coord)

    return p.within(poly)


def stationLoc_henkan(source_loc_filepath, target_loc_filepath, city_polygon_filepath):

    # geojsonファイルを読み込む
    with open(source_loc_filepath, 'r') as f:
        station_loc_all = json.load(f)

    # 'geometry'の座標を複数点の中心にする(station_loc_allを変更)
    for item in station_loc_all['features']:
        item['geometry']['type']='Point'
        average_point = avg_point(item['geometry']['coordinates'])
        item['geometry']['coordinates'] = average_point

    # 指定した都市のポリゴンを読み込む
    with open(city_polygon_filepath, 'r') as f:
        city_poly = json.load(f)

    city_coord = [tuple(coord) for coord \
        in city_poly['features'][0]['geometry']['coordinates'][0]]

    # featuresのリストから指定した都市に該当するもののみ取り出す
    station_loc_target={}
    station_loc_target['type']='FeatureCollection'
    station_loc_target['features'] = []

    for geojson_feature in station_loc_all['features']:
        point = geojson_feature['geometry']['coordinates']
        if point_within_polygon(point, city_coord):
            station_loc_target['features'].append(geojson_feature)

    # 鉄道駅の位置:station.geojson(パパマママップ)用に形式を変更
    for item in station_loc_target['features']:
        prop = item['properties']

        # Idの追加
        prop['Id'] = 0

        # 項目名の変更
        prop['line'] = prop.pop('N02_003') # N02_003 -> line
        prop['company'] = prop.pop('N02_004') # N02_004 -> company
        prop['station_name'] = prop.pop('N02_005') # N02_005 -> station_name
 
        # shubetsuの追加
        prop['shubetsu'] = prop['company']

        # lon, latの追加
        prop['lon'] = item['geometry']['coordinates'][0]
        prop['lat'] = item['geometry']['coordinates'][1]

    # geojsonファイルに出力
    with open(target_loc_filepath, 'w') as f:
        json.dump(station_loc_target, f, ensure_ascii=False, indent=4)

    # 戻り値
    return station_loc_target


if __name__ == '__main__':

    # 動作テスト(N03)
    source_filepath_N03 = './test/N03-19_13_190101.geojson'
    target_filepath_N03 = './test/city_polygon.geojson'
    prefecture_name = '東京都'
    city_name = '八王子市'

    display(district_henkan(source_filepath_N03, target_filepath_N03, \
        prefecture_name, city_name))

    # 動作テスト(A27_1)
    source_loc_filepath_A27 = './test/A27P-16_13.geojson'
    target_loc_filepath_A27 = './test/Elementary_loc.geojson'
    source_poly_filepath_A27 = './test/A27-16_13.geojson'
    target_poly_filepath_A27 = './test/Elementary.geojson'
    city_name = '八王子市'

    display(elementaryLoc_henkan(source_loc_filepath_A27, \
        target_loc_filepath_A27, city_name))
    display(elementaryPoly_henkan(source_poly_filepath_A27, \
        target_poly_filepath_A27, target_loc_filepath_A27, city_name))

    # 動作テスト(A32)
    source_loc_filepath_A32 = './test/A32P-16_13.geojson'
    target_loc_filepath_A32 = './test/Middleschool_loc.geojson'
    source_poly_filepath_A32 = './test/A32-16_13.geojson'
    target_poly_filepath_A32 = './test/Middleschool.geojson'
    city_name = '八王子市'

    display(middleschoolLoc_henkan(source_loc_filepath_A32, \
        target_loc_filepath_A32, city_name))

    display(middleschoolPoly_henkan(source_poly_filepath_A32, \
        target_poly_filepath_A32, target_loc_filepath_A32, city_name))

    # 動作テスト(N02)
    source_loc_filepath_N02 = './test/N02-17_Station.geojson'
    city_filepath_N02 = './test/city_polygon.geojson'
    target_loc_filepath_N02 = './test/station.geojson'

    display(stationLoc_henkan(source_loc_filepath_N02, \
        target_loc_filepath_N02, city_filepath_N02))


#%%
