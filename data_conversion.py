#%%
"""
行政区域のデータ(geojson形式)を読み込んで、指定した都市市の行政区域のデータのみ取り出して
Papamamaマップにあう形式のファイル(geojson形式)にして出力
"""

#%%
# モジュールインポート
from pathlib import Path
import sys

from modules import ksj_papamama
from modules import nursery_hachioji_papamama


#%%
# パラメータ設定
prefecture_name = '東京都'
city_name = '八王子市'
pathname_dataorig = './data_orig/'

#%%
# data_origディレクトリに必要なファイルが揃っているかをチェック

def file_exist(pathname, file_expression):
    p = Path(pathname)
    try:
        file_pathname = str(list(p.glob(file_expression))[0])
        print(file_pathname, ": found")
        return file_pathname
    except:
        print(file_expression, ": not found")
        return None

# 変換元のファイルのパス指定
source_filepath_N03 = file_exist(pathname_dataorig, "N03-*.geojson")
source_poly_filepath_A27 = file_exist(pathname_dataorig, "A27-*.geojson")
source_loc_filepath_A27 = file_exist(pathname_dataorig, "A27P-*.geojson")
source_poly_filepath_A32 = file_exist(pathname_dataorig, "A32-*.geojson")
source_loc_filepath_A32= file_exist(pathname_dataorig, "A32P-*.geojson")
source_loc_filepath_N02 = file_exist(pathname_dataorig, "N02-*_Station.geojson")
source_filepath_nurseryhachioji = file_exist(pathname_dataorig, "kosodateshisetuitiran.xlsx")
#source_filepath_nurseryhachioji = './data_orig/kosodateshisetuitiran.xlsx'

# 変換後のファイルのパス指定
target_filepath_N03 = './data/city_polygon.geojson'
target_loc_filepath_A27 = './data/Elementary_loc.geojson'
target_poly_filepath_A27 = './data/Elementary.geojson'
target_loc_filepath_A32 = './data/Middleschool_loc.geojson'
target_poly_filepath_A32 = './data/Middleschool.geojson'
target_loc_filepath_N02 = './data/station.geojson'
city_filepath_N02 = target_filepath_N03
    
target_csv_filepath_nurseryhachioji = './data_orig/nurseryFacilities.csv'
target_geojson_filepath_nurseryhachioji = './data/nurseryFacilities.geojson'


#%%
# N03:行政区域データを変換
try:
    ksj_papamama.district_henkan(source_filepath_N03, target_filepath_N03, \
        prefecture_name, city_name)
    print(target_filepath_N03, ": file translation complete")
except:
    print(target_filepath_N03, ": file translation Error")


# A27:小学校の位置情報データ, ポリゴンデータを変換
try:
    ksj_papamama.elementaryLoc_henkan(source_loc_filepath_A27, \
        target_loc_filepath_A27, city_name)
    print(target_loc_filepath_A27, ": file translation complete")
except:
    print(target_loc_filepath_A27, ": file translation Error")

try:
    ksj_papamama.elementaryPoly_henkan(source_poly_filepath_A27, \
        target_poly_filepath_A27, target_loc_filepath_A27, city_name)
    print(target_poly_filepath_A27, ": file translation complete")
except:
    print(target_poly_filepath_A27, ": file translation Error")


# A32:中学校の位置情報データ,ポリゴンデータを変換
try:
    ksj_papamama.middleschoolLoc_henkan(source_loc_filepath_A32, \
        target_loc_filepath_A32, city_name)
    print(target_loc_filepath_A32, ": file translation complete")
except:
    print(target_loc_filepath_A32, ": file translation Error")

try:
    ksj_papamama.middleschoolPoly_henkan(source_poly_filepath_A32, \
        target_poly_filepath_A32, target_loc_filepath_A32, city_name)
    print(target_poly_filepath_A32, ": file creation complete")
except:
    print(target_poly_filepath_A32, ": file creation Error")

# N02:駅の位置情報データを変換
try:
    ksj_papamama.stationLoc_henkan(source_loc_filepath_N02, \
        target_loc_filepath_N02, city_filepath_N02)
    print(target_loc_filepath_N02, ": file translation complete")
except:
    print(target_loc_filepath_N02, ": file translation Error")

#%%
# 保育園データを変換
try:    
    nursery_hachioji_papamama.henkan_nursely_hachioji(source_filepath_nurseryhachioji, \
            target_csv_filepath_nurseryhachioji, target_geojson_filepath_nurseryhachioji)
    print(target_geojson_filepath_nurseryhachioji, ": file translation complete")
except:
    print(target_geojson_filepath_nurseryhachioji, ": file translation Error")


#%%
