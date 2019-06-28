
# モジュールインポート
import requests
import xml.etree.ElementTree as ET
from pathlib import Path


# 最新のzipファイルダウンロードURLを取得する
def get_ksj_zipurl_latest(url_base, params_dict):
    zipurl_dict={}
    for elem in params_dict.keys():
        zipurl_dict[elem] = get_ksj_zipurl(url_base,params_dict[elem])[-1]
    
    return zipurl_dict

# zipファイルダウンロード用のURLを取得する
def get_ksj_zipurl(url_base, params):
    response = requests.get(url_base, params)
    xml_string = response.text
    root = ET.fromstring(xml_string)
    zipurl_list =[]

    for elem in root.iter('zipFileUrl'):
        zipurl_list.append(elem.text)
    
    return zipurl_list


# 指定したURLからファイルをダウンロードする
def download(url, save_directory_path):
    file_name = Path(url).name
    p_dir = Path(save_directory_path)

    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(p_dir / file_name, 'wb') as file:
            for chunk in res.iter_content(chunk_size=1024):
                file.write(chunk)