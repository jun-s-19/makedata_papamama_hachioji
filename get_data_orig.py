#%%

"""
Papamama保育園マップに必要な元データをダウンロードする
(国土数値情報データは解凍して、shapeからgeojsonファイルに変換する）
    - ダウンロードデータ一時格納先：'./temp/'
    - ダウンロードファイル一覧
        * 国土数値情報　小学校区データ: A27-**_GML.zip
        * 国土数値情報　中学校区データ: A32-**_GML.zip
        * 国土数値情報　鉄道データ: N02-**_GML.zip
        * 国土数値情報　行政区域データ: N03-**_GML.zip
        * 八王子市子育て関連オープンデータ>子育て施設一覧 :kosodateshisetuitiran.xlsx
    - 変換したファイルの格納先: './data_orig/'
"""
#%%
# モジュールインポート
import requests
import xml.etree.ElementTree as ET
import pathlib
from pathlib import Path
import glob
import shutil
import subprocess
from tqdm import tqdm

from modules import ksj_download
#%%
# Pathのパラメータ設定
path_temp = './temp/'
p_temp = Path("./temp/")
p_dest = Path("./data_orig/")

# 国土数値情報取得用のURL, パラメータ
url_ksj_base = 'http://nlftp.mlit.go.jp/ksj/api/1.0b/index.php/app/getKSJURL.xml'
params_ksj_dict={}
params_ksj_dict['N03'] = {
    'appId': 'ksjapibeta1', 
    'lang': 'J',
    'dataformat':'1',
    'identifier':'N03',
    'prefCode':'13',
    'fiscalyear':'2000-2020',
    }
params_ksj_dict['A27'] = {
    'appId': 'ksjapibeta1',
    'lang': 'J',
    'dataformat':'1',
    'identifier':'A27',
    'prefCode':'13', 
    'fiscalyear':'2000-2020',
    }
params_ksj_dict['A32'] = {
    'appId': 'ksjapibeta1',
    'lang': 'J',
    'dataformat':'1',
    'identifier':'A32',
    'prefCode':'13',
    'fiscalyear':'2000-2020',
    }
params_ksj_dict['N02'] = {
    'appId': 'ksjapibeta1',
    'lang': 'J',
    'dataformat':'1',
    'identifier':'N02',
    'fiscalyear':'2000-2020',
    }

# 保育園オープンデータダウンロード用URL
url_nursely = "https://www.city.hachioji.tokyo.jp/contents/open/002/p005871_d/fil/kosodateshisetuitiran.xlsx"



#%%
# tempフォルダを作成する
p_temp.mkdir(exist_ok=True)

#%%
# zipファイルをダウンロードする
zipurl_dict = ksj_download.get_ksj_zipurl_latest(url_base=url_ksj_base, params_dict=params_ksj_dict)

for url in tqdm(zipurl_dict.values()):
    ksj_download.download(url, path_temp)
    print("Download complete: ",url)

#%%
# ./temp/のzipファイルをunarコマンドで解凍する
zipfiles = list(p_temp.glob("*.zip"))

for zipfile in zipfiles:
    check = subprocess.run(["unar", "-o", "./temp/", str(zipfile),"-q"])
    print(zipfile,": unzip complete,", "return code:",check.returncode)

#%%
# tempのディレクトリ一覧を取得する
unzip_directory_paths = []
for elem in p_temp.iterdir():
    if Path(elem).is_dir():
        unzip_directory_paths.append(elem)

#%%
# geojsonファイルを作成する
for p in unzip_directory_paths:
    if p.name.startswith('N03') or p.name.startswith('N02'):
        # N02, N03のgeojsonファイルをdata_origへコピーする
        for geojsonfile in p.glob("*.geojson"):
            shutil.copy(str(geojsonfile),"./data_orig/")
            print(str(geojsonfile.name)," : file creation complete")

    elif p.name.startswith('A27') or p.name.startswith('A32'):
        # A27, A32にあるshapefileは変換する
        shapefiles = p.glob("**/*.shp")
        for shapefile in shapefiles:
            name = shapefile.name
            file_geojson = p_dest/(shapefile.name)
            file_geojson = file_geojson.with_suffix(".geojson")
            check = subprocess.run(["ogr2ogr", "-f", "GeoJSON", \
                file_geojson, shapefile, "-oo", "ENCODING=CP932"])
            if check.returncode == 0:
                print(str(file_geojson.name), ": file creation complete")
            else:
                print(str(file_geojson.name), ": file creation Error,", "return code:", check.returncode)
    else:
        pass


#%%    
# tempフォルダを中身ごと削除する
shutil.rmtree("./temp/")
print('./temp/: directory deleted')

#%%
# 保育園のデータをダウンロードする
ksj_download.download(url_nursely, "./data_orig/")
print("Download complete: ", url_nursely)

#%%
