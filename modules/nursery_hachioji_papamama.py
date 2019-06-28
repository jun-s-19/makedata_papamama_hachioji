#%%
'''
八王子市の保育施設一覧(Excel)のオープンデータを
保育所マップのアプリであるPapamamaマップ用に変換する関数群を作成。
最初にCSV形式にして出力し、次にそのファイルをgeojson形式に変換します。
https://www.city.hachioji.tokyo.jp/contents/open/002/p005871.html

'''
#%%
# モジュールのインポート
import pandas as pd
import numpy as np
import json
import csv
from collections import OrderedDict
import time
from IPython.core.display import display


dict_nursery_type ={
    '事業所内保育事業':'認可外',
    '家庭的保育者':'認可外',
    '小規模保育事業':'認可保育所',
    '東京都認証保育所':'認可外',
    '私立幼稚園':'幼稚園',
    '認定こども園（地方裁量型）':'認可保育所',
    '認定公立保育所':'認可保育所',
    '認定私立保育所':'認可保育所',
}

def split_StartEnd(str):
    if 'から' in str:
        return str.split('から')
    elif '～' in str:
        return str.split('～')
    else:
        return [str,'']


def extract_AgeS(str):
    return split_StartEnd(str)[0].replace('クラス','')


def extract_AgeE(str):
    return split_StartEnd(str)[1].replace('クラス','')


def correct_tel(tel_str):
    if type(tel_str) == type(str):
        return tel_str.replace('－','-') # 全角のハイフンを半角のハイフンに統一
    else:
        return None


def extract_Ownership(type):
    if '私立' in type:
        return '私'
    elif '公立' in type:
        return '公'
    else:
        return None


def henkan_nursely_hachioji(source_filepath, target_csv_filepath, target_geojson_filepath):

    df_orig = pd.read_excel(source_filepath)
    df = df_orig.copy()

    # 不要なカラムを削除する
    df = df.drop(['都道府県コード又は市区町村コード','都道府県名', '市区町村名','内線番号'], axis=1)

    # ’Shanai', 'Kodomo'の列を作る
    df['Shanai'] = (df['種別']=='事業所内保育事業').map({True:'Y',False:None})
    df['Kodomo'] = (df['種別']=='認定こども園（地方裁量型）').map({True:'Y',False:None})

    # 'Type'の列を作る
    df['Type'] =(df['種別']).map(dict_nursery_type)

    # 'Name'の列を作る
    df['Name'] = df['名称'].map(lambda str: str.replace('\u3000','')) # 全角空白を削除する

    # 'Label'の列を作る
    df['Label'] = df['Name'] # 現状は'Name'と同一にする

    # AgeS(保育開始年齢), AgeE(保育終了年齢)の列を作成する
    df['AgeS'] = df['受入年齢'].map(extract_AgeS)
    df['AgeE'] = df['受入年齢'].map(extract_AgeE)

    # 'Full'(定員)の列を作成する
    df['Full'] = df['収容定員']

    # 'Open'（開園時間）,'Close'（閉園時間）の列を作成する
    df['Open'] = df['開始時間'].map(lambda time: time.strftime('%H:%M'))
    df['Close'] = df['終了時間'].map(lambda time: time.strftime('%H:%M'))

    # 'H24'の列を作成する
    df['H24'] = (df.Open=='00:00')&(df.Close=='00:00')
    df['H24'] = df['H24'].map({True:'Y',False:None})

    # 'Memo'の列を作成する
    df['Memo'] = df['利用可能日時特記事項']

    # 'Extra'の列を作成する
    df['Extra'] = None # 現状はnullとする

    # 'Temp'の列を作成する
    df['Temp'] = df['一時預かりの有無'].map({'有':'Y','無':None,np.nan:None})

    # 'Holiday'の列を作成する
    df['Holiday'] = None

    # 'Night'の列を作成する
    df['Night'] = None

    # 'Add1','Add2'の列を作成する
    df['Add1'] = '八王子市'
    df['Add2'] = df['住所'].map(lambda str: str.replace('東京都','').replace('八王子市',''))

    # 'TEL','FAX'の列を作成する
    df['TEL'] = df['電話番号'].map(correct_tel)
    df['FAX'] = df['FAX番号'].map(correct_tel)

    # 'Owner'の列を作成する
    df['Owner'] = df['団体名']

    # 'Ownership'の列を作成する
    df['Ownership'] = df['種別'].map(extract_Ownership)

    # 'Proof'の列を作成する
    df['Proof'] = None

    # Y(緯度), X(経度)の列を作成する
    df['Y'] = df['緯度']
    df['X'] = df['経度']

    # 'url'の列を作成する
    df['url'] = df['URL'].map(lambda x: None if pd.isnull(x) else x)

    # 'Vacancy', 'VancancyDate'の列を作成する
    df['Vacancy'] = None
    df['VacancyDate'] = None

    # latitude,longitude,altitude,geometryの列を作成する(csv用)
    df['latitude'] = df['Y']
    df['longitude'] = df['X']
    df['altitude'] = None
    df['geometry'] = 'Point'

    # HIDの列を作成する
    df['HID'] = df['NO']+1000 

    # map用のデータフレームを作成する
    df_map = df[['latitude','longitude','altitude','geometry','HID',\
        'Type','Kodomo','Name','Label','AgeS','AgeE','Full','Open',\
        'Close','H24','Memo','Extra','Temp','Holiday','Night',\
        'Add1','Add2','TEL','FAX','Owner','Ownership','Proof',\
        'Shanai','Y','X','url','Vacancy','VacancyDate']]

    # 一時的にCSVファイルに保存する
    df_map.to_csv(target_csv_filepath,header=True, index=False)

    # 辞書形式で読み込む
    json_list = []
    with open(target_csv_filepath,'r') as f:
        for row in csv.DictReader(f):
            json_list.append(row)

    # 座標の値を文字列から浮動点小数に変更する
    # 定員(Full)の値を文字列から整数に変更する
    for item in json_list:
        str_X = item['X']
        str_Y = item['Y']
        str_latitude = item['latitude']
        str_longitude = item['longitude']
        str_Full = item['Full']
        
        item['X'] = float(str_X)
        item['Y'] = float(str_Y)
        item['latitude'] = float(str_latitude)
        item['longitude'] = float(str_longitude)
        item['Full'] = int(str_Full)

    # ""をNoneに変換する
    for item in json_list:
        for key in item.keys():
            if item[key] == "":
                item[key] = None

    nursery_hachioji={}
    nursery_hachioji['type']='FeatureCollection'
    nursery_hachioji['features'] = []

    # geojson用に形式を整える
    for ordered_dict in json_list:
        
        new_ordered_dict = OrderedDict()
        new_ordered_dict['type'] = "Feature"

        new_ordered_dict['geometry'] = {}
        new_ordered_dict['geometry']['type'] = 'Point'
        new_ordered_dict['geometry']['coordinates'] = [ordered_dict['longitude'], ordered_dict['latitude']]

        del ordered_dict['latitude'], ordered_dict['longitude'], ordered_dict['altitude']
        del ordered_dict['geometry']
        new_ordered_dict['properties'] = ordered_dict

        nursery_hachioji['features'].append(new_ordered_dict)

    # geojsonファイルを保存
    with open(target_geojson_filepath, 'w') as f:
        json.dump(nursery_hachioji, f, ensure_ascii=False, indent=4)

    # 戻り値
    return nursery_hachioji


if __name__ == '__main__':
    source_filepath_hachioji = './test/kosodateshisetuitiran.xlsx'
    target_csv_filepath_hachioji = './test/nurseryFacilities.csv'
    target_geojson_filepath_hachioji = './test/nurseryFacilities.geojson'

    henkan_nursely_hachioji(source_filepath_hachioji, \
        target_csv_filepath_hachioji, target_geojson_filepath_hachioji)

