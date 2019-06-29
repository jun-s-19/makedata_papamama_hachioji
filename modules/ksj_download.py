"""
国土数値情報データダウンロードサービスからデータをダウンロードする際に
利用する関数群を定義
"""

# モジュールインポート
import requests
import xml.etree.ElementTree as ET
from pathlib import Path


def get_ksj_zipurl_latest(url_base, params_dict):
    """最新のzipファイルダウンロードURLを取得する
    
    Parameters
    ----------
    url_base : [url]
        Web APIのベースとなるURL
    params_dict : dict
        クエリのパラメータ(dict)の辞書
    
    Returns
    -------
    [url]
        最新のzipファイルダウンロードURL
    """
    zipurl_dict={}
    for elem in params_dict.keys():
        zipurl_dict[elem] = get_ksj_zipurl(url_base,params_dict[elem])[-1]
    
    return zipurl_dict

# 
def get_ksj_zipurl(url_base, params):
    """zipファイルダウンロード用のURLを取得する
    
    Parameters
    ----------
    url_base : [url]
        Web APIのベースとなるURL
    params : [dict]
        クエリのパラメータ
    
    Returns
    -------
    [list]
        'zipFileUrl'に対応する値のリスト
    """
    response = requests.get(url_base, params)
    xml_string = response.text
    root = ET.fromstring(xml_string)
    zipurl_list =[]

    for elem in root.iter('zipFileUrl'):
        zipurl_list.append(elem.text)
    
    return zipurl_list


# 
def download(url, save_directory_path):
    """指定したURLからファイルをダウンロードする
    
    Parameters
    ----------
    url : [str]
        ダウンロード対象のURL
    save_directory_path : [str]
        ダウンロードしたファイルを格納するディレクトリのパス名
    """
    file_name = Path(url).name
    p_dir = Path(save_directory_path)

    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(p_dir / file_name, 'wb') as file:
            for chunk in res.iter_content(chunk_size=1024):
                file.write(chunk)
    else:
        print("Download Error. Response status:", res.status_code)