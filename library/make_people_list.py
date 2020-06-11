import json
import csv
from typing import List

from library.directory_control import get_file_dir_path


# json 파일이 여러개일 때 입력받아 하나의 dict으로 합침
def json_file_input(jsonDirList: list) -> dict:
    json_data = dict()
    for jsonDir in jsonDirList:
        with open(jsonDir, 'rt', encoding='utf-8') as file:
            json_element = json.load(file)
            for key in json_element["people_mapping"]:
                json_data[key] = json_element["people_mapping"][key]

    return json_data


# json이 list로 구성되어 있을 때, 각 json data마다 다른 file로 출력
def json_file_output(jsonDataDir: list, jsonList: List[dict]) -> None:
    for i, jsonDir in enumerate(jsonDataDir):
        with open(jsonDir, 'wt', encoding="utf-8") as file:
            json.dump(jsonList[i], file, indent=4, ensure_ascii=False)  # dict -> json


# csv 파일이 여러개일 때 입력받아 하나의 dict으로 합침
def csv_file_input(csvDirList: list) -> dict:
    csv_data = dict()
    for i, csvDir in enumerate(csvDirList):
        with open(csvDir, 'rt', encoding='cp949') as file:
            reader = csv.reader(file)
            for row in reader:
                csv_data[row[0]] = row[1:]

    return csv_data


def set_people_list(json_data: dict, csv_data: dict) -> list:
    """
    list1(PeopleList.1toN.json) =
            {main character name : [sub character name1, name2, ...],
             main character name2: [sub character name1, name2, ...],
             ...}
    list2(PeopleList.Nto1.json) =
            {sub character name1: main character name,
             sub character name2: main character name,
             ...}
    """
    list1 = dict()
    list2 = dict()
    for name in json_data.keys():
        list1[name] = csv_data[name]
        for element in csv_data[name]:
            if element != "":
                list2[element] = name

    people_list = [list1, list2]
    return people_list


def get_people_list() -> list:
    lifecycle_path = ['metadata', 'lifecycle']

    # read json data
    file_name_list = ["1001.metadata-character.json"]
    metadata_dir = get_file_dir_path(file_name_list, lifecycle_path)
    json_data = json_file_input(metadata_dir)

    # read csv data
    csv_name_list = ["PeopleMappingTable.csv"]
    csv_data_dir = get_file_dir_path(csv_name_list, lifecycle_path)

    csv_data = csv_file_input(csv_data_dir)
    
    # make people_list
    people_list = set_people_list(json_data, csv_data)

    # print peopleList to json file
    people_list_name = ["PeopleList.1toN.json", "PeopleList.Nto1.json"]
    people_list_dir = get_file_dir_path(people_list_name, lifecycle_path)

    json_file_output(people_list_dir, people_list)

    # peopleList return
    return people_list


if __name__ == '__main__':
    print(get_people_list())
