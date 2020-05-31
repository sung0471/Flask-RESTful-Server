import os
import platform
from typing import Union, Optional, List

nowdir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(os.path.dirname(nowdir))


def metadata_file_init(fileNameList):
    metadata_dir_dict = {
        'Windows': [basedir+"\\metadata\\"],
        'Linux': [basedir+"/metadata/"]
    }

    for osName in metadata_dir_dict:
        metadata_dir = metadata_dir_dict[osName][0]
        metadata_dir_list = list()
        for fileName in fileNameList:
            metadata_dir_list.append(metadata_dir + fileName)
        metadata_dir_dict[osName] = metadata_dir_list

    return metadata_dir_dict


def check_os(metadataDir):
    my_os = platform.system()
    if my_os in list(metadataDir.keys()):
        return metadataDir[my_os]
    else:
        raise FileNotFoundError


# return extended file_name or file_path
def get_extended_path(origin: str, mid: str = '.', extra: str = 'new'):
    file_name, ext = os.path.splitext(origin)
    return file_name + mid + extra + ext


# `19.3.28 add
# os에 따른 구분 제거 / check_os 함수 사용할 필요 없음
def get_metadata_dir_path(file_name_list: Union[List[str], str], dir_route: Optional[Union[List[str], str]] = None)\
        -> Union[List[str], str]:
    """
    file_name_list:
        파일 경로 or 파일 경로의 리스트
        list of file path or file path
    dir_route:
        sub directory의 경로 리스트 or sub directory name or None
        None or list of sub directory path or directory path
    return:
        메타데이터 파일 경로 or 파일 경로의 리스트
        metadata file path or list of file path
    """
    metadata_dir = os.path.join(basedir, 'metadata')
    if dir_route is not None:
        if isinstance(dir_route, list):
            metadata_base = os.path.join(*dir_route)
        else:
            metadata_base = dir_route
        metadata_dir = os.path.join(metadata_dir, metadata_base)

    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)

    if isinstance(file_name_list, list):
        metadata_path_list = list()
        for fileName in file_name_list:
            metadata_path_list.append(os.path.join(metadata_dir, fileName))
        return metadata_path_list
    else:
        metadata_path = os.path.join(metadata_dir, file_name_list)
        return metadata_path
