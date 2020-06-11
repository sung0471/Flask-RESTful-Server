"""
Description
    Returns metadata(time, place, script, person) corresponding to a specific time of video
"""

from flask import Flask, make_response, render_template
from flask_restful import Resource, Api, reqparse
from library.directory_control import get_file_dir_path

import os
import json
import csv
from collections import OrderedDict

project_name = 'view'
metadata_path = get_file_dir_path(project_name, 'metadata')
template_path = get_file_dir_path(project_name, 'templates')
app = Flask(__name__, template_folder=template_path, static_folder=metadata_path)
api = Api(app)

filename_list = os.listdir(metadata_path)
filename = [file for file in filename_list if 'scenario' in file]
filename_new = [file for file in filename_list if 'result' in file]
file_num = len(filename)  # json 파일 개수
metadata_dir_list = get_file_dir_path(filename, metadata_path)

data = [{}] * file_num  # scenario 전체 데이터
ACT = [{}] * file_num  # 각 scenario의 ACT 전체 데이터
act_length = [0] * file_num  # ACT 배열의 각 요소 별 개수

arr_keyword = [[] for _ in range(file_num)]  # 각 scenario의 act별 keyword에 해당하는 dictionary 배열
keyword_length = [0] * file_num

arr_sc = [[] for _ in range(file_num)]  # 각 scenario의 scene 데이터 배열
sc_num_range = [0] * file_num  # 각 scenario별 scene number의 최댓값을 저장한 배열

# json파일 읽어서 저장
for scenario_num, metadata_dir in enumerate(metadata_dir_list):
    with open(metadata_dir, 'rt', encoding='UTF-8') as data_file:
        data[scenario_num] = json.load(data_file)  # 각 Scenario1~4.json 파일의 데이터를 배열로 받음(dictionary)
        ACT[scenario_num] = data[scenario_num]["ACT"]  # 각 scenario에서 "ACT"를 key로 가진 value를 받음
        # 즉, ACT 전체를 받음

        act_length[scenario_num] = len(ACT[scenario_num])  # 각 scenario별 act의 개수
        for i in range(act_length[scenario_num]):
            arr_keyword[scenario_num].extend(ACT[scenario_num][i]["Keyword"])  # 각 scenario별 keyword data 저장

        keyword_length[scenario_num] = len(arr_keyword[scenario_num])
        # 각 scenario별 keyword의 개수
        for i in range(keyword_length[scenario_num]):
            arr_sc[scenario_num].extend(arr_keyword[scenario_num][i]["SC"])  # 각 scenario별 Scene data 저장

        sc_num_range[scenario_num] = len(arr_sc[scenario_num])  # 각 Scenario별 Scene의 개수

# PEOPLE, PLACE, SCRIPT, TIME : 입력받을 키워드를 갖는 변수
# PEOPLE_LIST : annotation할 인물들의 리스트
# KEY_LIST : keyword 변수들의 배열
PEOPLE = "people"
PLACE = "where"
SCRIPT = "script"
TIME = "when"
KEY_LIST = [PEOPLE, PLACE, SCRIPT, TIME]

person_info_files = dict()
for file in filename_list:
    file_name, ext = os.path.splitext(file)
    if ext == '.csv':
        if file_name == 'person_name_url':
            person_info_files[file_name] = file
        else:
            person_info_files['person_info'] = file


people_list = []
people_list_for_uri = []
person_data = {"TITLE": ""}
with open(get_file_dir_path(person_info_files['person_name_url'], metadata_path), 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    all_lines = []
    for line in reader:
        all_lines.append(line)

    people_list = all_lines[0]
    people_list_for_uri = all_lines[1]
for person in people_list:
    person_data[person] = ""

with open(get_file_dir_path(person_info_files['person_info'], metadata_path), 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    index = 0
    for line in reader:
        if index == 0:
            line[0] = '이름'
            person_data["TITLE"] = line
        else:
            person_data[line[0]] = line
        index += 1
        if index == 7:
            break

character_dir = 'character'


# 값의 범위를 체크하는 함수
def range_check(value, range1, range2=None):
    if range2 is None:  # 값의 범위를 list로 받는 경우
        if value in range1:
            return True
        else:
            return False
    else:  # start, end 값으로 받는 경우
        if range1 <= value <= range2:
            return True
        else:
            return False


# 값의 범위들을 모두 체크하는 함수
def key_check(scenario_num, sc_num, treatment_key):
    if range_check(scenario_num, 1, 4) and range_check(sc_num, 1, sc_num_range[scenario_num - 1]) \
            and range_check(treatment_key.lower(), KEY_LIST):
        return True
    else:
        return False


def get_description(description_type=None):
    assert description_type in ['api', 'index', 'person']
    if description_type == 'api':
        dict_data = dict()
        dict_data['/scenario/<int:scenario_num>'] = 'JSON 데이터를 전부 출력'
        dict_data['/act/<int:scenario_num>'] = 'JSON 파일의 key인 "ACT"의 values을 출력'
        dict_data['/act/<int:scenario_num>/<int:act_num>'] = '한 시나리오의 ACT 하나를 출력'
        dict_data['/keyword/<int:scenario_num>'] = '특정 시나리오의 ACT > Keyword에 해당하는 모든 values을 출력'
        dict_data['/scene/<int:scenario_num>'] = '특정 시나리오의 ACT > Keyword > SC에 해당하는 모든 values을 출력'
        dict_data['/raw/<int:scenario_num>/<int:sc_num>/<string:treatment_key>'] = \
            'ACT > Keyword > SC > Treatment > treatment_key, values의 값<br>' \
            '특정 Scenario, Scene, treatment_key에 해당하는 값을 모두 JSON으로 출력'
        dict_data['/html/<int:scenario_num>/<int:sc_num>/<string:treatment_key>'] = \
            'ACT > Keyword > SC > Treatment > treatment_key, values의 값<br>' \
            '특정 Scenario, Scene, keyword에 해당하는 값을 중복제거하여 HTML template 출력'
        dict_data['/json/<int:scenario_num>/<int:sc_num>/<string:treatment_key>'] = \
            'ACT > Keyword > SC > Treatment > treatment_key, values의 값<br>' \
            '특정 Scenario, Scene, keyword에 해당하는 값을 중복제거하여 JSON 데이터 출력'

        dict_data['/html/<string:name>'] = '사람이름 키워드를 받으면 그에 맞는 사람 정보를 HTML template 출력'
        dict_data['/json/<string:name>'] = '사람이름 키워드를 받으면 그에 맞는 사람 정보를 JSON 데이터 출력'

        dict_data['/lovew?current_time=h:mm:ss'] = '재생 시간에 따른 데이터 출력'

        api_error_msg = '<h2>RESTful API List</h2>'
        api_error_msg += '<table border="1" style="border-collapse:collapse">'
        for key, value in dict_data.items():
            new_key = str()
            for char in key:
                if char == '<':
                    new_key += '&lt;'
                elif char == '>':
                    new_key += '&gt;'
                else:
                    new_key += char
            api_error_msg += '<tr><td>{}</td> <td>{}</td></tr>'.format(new_key, value)
        api_error_msg += '</table>'

        return api_error_msg

    elif description_type == 'index':
        index_error_msg = [["Range of Scene", "Start", "End"],
                            ["Scenario 1", 1, len(arr_sc[0])],
                            ["Scenario 2", 1, len(arr_sc[1])],
                            ["Scenario 3", 1, len(arr_sc[2])],
                            ["Scenario 4", 1, len(arr_sc[3])],
                            ["Usable Keyword", "People / Where / When / Script"],
                            ["Keyword는 대소문자 구분하지 않음"]]

        return index_error_msg

    else:
        person_name_url_matching = \
            ["{} : {}".format(person, person_url) for person, person_url in zip(people_list, people_list_for_uri)]
        person_error_msg = [["Person name List"],
                            person_name_url_matching[:3],
                            person_name_url_matching[3:]]

        return person_error_msg


class ApiDescription(Resource):
    def get(self):
        api_description = get_description('api')

        res = make_response(api_description)
        res.headers['Content-type'] = 'text/html; charset=utf-8'
        return res


class RestfulException(Exception):
    def __init__(self):
        super().__init__('Flask-RESTful Resource Key Error')

    def __str__(self):
        return 'Flask-RESTful Resource Key Error'


class GetRawData(Resource):
    def get(self, json_type=None, scenario_num=None, act_num=None):
        json_type_list = ['scenario', 'act', 'keyword', 'scene']
        try:
            if json_type is None or json_type not in json_type_list or scenario_num is None:
                raise RestfulException
            else:
                if json_type == 'scenario':
                    out_data = data[scenario_num - 1]
                elif json_type == 'act':
                    if act_num is None:
                        out_data = ACT[scenario_num - 1]
                    else:
                        out_data = ACT[scenario_num - 1][act_num - 1]
                elif json_type == 'keyword':
                    out_data = arr_keyword[scenario_num - 1]
                else:
                    out_data = arr_sc[scenario_num - 1]

            json_data = json.dumps(out_data, ensure_ascii=False)
            res = make_response(json_data)
            res.headers['Content-type'] = 'application/json'

        except RestfulException:
            api_description = get_description('api')
            res = make_response(api_description)
            res.headers['Content-type'] = 'text/html; charset=utf-8'

        return res


class GetInfo(Resource):
    def get(self, data_type, scenario_num, sc_num, treatment_key):
        error_type = None
        try:
            if data_type not in ['raw', 'html', 'json']:
                raise RestfulException

            # 입력된 index와 key의 유효체크
            if key_check(scenario_num, sc_num, treatment_key):
                treatment_key = treatment_key.lower()
            else:
                raise IndexError

        except RestfulException as e:
            error_type = 'api'

            print("Error : ", e)

        except IndexError as e:
            error_type = 'index'
            # indexError를 체크해서 올바른 index를 알려줌
            print("Error : ", e)
            detail_data = get_description(error_type)

        else:
            arr_data = arr_sc[scenario_num - 1][sc_num - 1]["Treatment"]  # 입력된 scenario와 scene에 맞는 treatments data
            data_length = len(arr_data)  # treatments의 개수
            detail_data = []  # 얻고자 하는 자세한 정보를 저장하는 배열

            find_key = []  # 입력된 key에 맞게 json에서 찾을 keys를 저장
            if treatment_key == SCRIPT:  # 대본
                find_key.append("script")
            elif treatment_key == PEOPLE:  # 인물
                find_key.append("S")
                find_key.append("O")
                find_key.append("withwhom")
            elif treatment_key == PLACE:  # 장소
                find_key.append("where")
            elif treatment_key == TIME:  # 시간
                find_key.append("when")

            for i in range(data_length):
                for key in find_key:
                    # print(i,key,arrData[i][key])
                    if data_type != 'raw':
                        if treatment_key == PEOPLE:
                            if arr_data[i][key] in people_list:  # 인물리스트에 있는 인물이 맞는 경우 저장
                                pass
                            else:
                                continue
                    detail_data.append(arr_data[i][key])  # treatment에서 원하는 key에 대응하는 값을 가져옴

            if data_type != 'raw':
                detail_data = list(OrderedDict.fromkeys(detail_data))  # 각 treatment별로 중복된 값 제거

        finally:
            if error_type == 'api':
                api_description = get_description(error_type)

                res = make_response(api_description)
                res.headers['Content-type'] = 'text/html; charset=utf-8'
            elif data_type == 'html' or error_type == 'index':
                # 미리 저장한 "get_info.html" template으로 상세정보를 출력
                res = make_response(render_template('get_info.html',
                                                    scenario_num=scenario_num, sc_num=sc_num,
                                                    treatment_key=treatment_key, detaildata=detail_data))
                res.headers['Content-type'] = 'text/html'
            else:
                json_data = json.dumps(detail_data, ensure_ascii=False, indent=2)
                res = make_response(json_data)
                res.headers['Content-type'] = 'application/json'

        return res


class GetInfoPerson(Resource):
    def get(self, data_type, person_name):
        detail_data = list()
        error_type = None
        try:
            if data_type not in ['html', 'json']:
                raise RestfulException

            # 입력된 이름 key의 유효체크
            if range_check(person_name.lower(), people_list_for_uri):
                pass
            else:
                real_name = ""
                raise IndexError

            real_name = people_list[people_list_for_uri.index(person_name)]

        except RestfulException as e:
            error_type = 'api'

            print("Error : ", e)

        except IndexError:
            error_type = 'person'

            # indexError를 체크해서 올바른 index를 알려줌
            print("person name validation error")
            detail_data = get_description(error_type)

        else:
            # 얻고자 하는 사람의 자세한 정보를 저장하는 배열
            detail_data = [person_data["TITLE"], person_data[real_name]]

        finally:
            if error_type == 'api':
                api_description = get_description(error_type)

                res = make_response(api_description)
                res.headers['Content-type'] = 'text/html; charset=utf-8'
            elif data_type == "html" or error_type == 'person':
                length = len(detail_data[0])
                # 19.3.19 revise
                # full_filename = characterDir + "/" + realname + ".png"
                full_filename = character_dir + "/" + person_name + ".png"

                # 미리 저장한 "get_info_person.html" template으로 상세정보를 출력
                res = make_response(render_template('get_info_person.html', name=real_name, detaildata=detail_data,
                                                    image=full_filename, length=length))
                res.headers['Content-type'] = 'text/html'
            else:
                json_data = json.dumps(detail_data, ensure_ascii=False, indent=2)
                res = make_response(json_data)
                res.headers['Content-type'] = 'application/json'

            return res


def return_metadata(current_time, dict):
    list = []
    for start_time in dict:
        if start_time <= current_time:
            for end_time in dict[start_time]:
                if current_time <= end_time:
                    for element in dict[start_time][end_time]:
                        list.append(element)
    return list


class LwMetadata(Resource):
    def get(self):
        lw_dict = []

        lw_dir_list = get_file_dir_path(filename_new, metadata_path)
        for i, metadata_dir in enumerate(lw_dir_list):
            with open(metadata_dir, 'rt', encoding='UTF-8') as data_file:
                lw_dict.append(json.load(data_file))

        res = reqparse.request.args
        if "current_time" in res.keys():
            current_time = res["current_time"]
            list_of_data = return_metadata(current_time, lw_dict[0])
            json_data = json.dumps(list_of_data, ensure_ascii=False, indent=2)
        else:
            json_data = json.dumps({"invalid": "invalid current time"}, ensure_ascii=False, indent=2)
        res = make_response(json_data)
        res.headers['Content-type'] = 'application/json'
        return res


api.add_resource(ApiDescription, '/')  # RESTful API List
api.add_resource(GetRawData,
                 '/<string:json_type>',
                 '/<string:json_type>/<int:scenario_num>',
                 '/<string:json_type>/<int:scenario_num>/<int:act_num>')
# /scenario/<int:scenario_num>      # JSON 데이터를 전부 출력
# /act/<int:scenario_num>           # JSON 파일의 key인 "ACT"의 values을 출력
# /act/<int:scenario_num>/<int:act_num>     # 한 시나리오의 ACT 하나를 출력
# /keyword/<int:scenario_num>       # 특정 시나리오의 ACT > Keyword에 해당하는 모든 values을 출력
# /scene/<int:scenario_num>         # 특정 시나리오의 ACT > Keyword > SC에 해당하는 모든 values을 출력

api.add_resource(GetInfo, '/<string:data_type>/<int:scenario_num>/<int:sc_num>/<string:treatment_key>')
# ACT > Keyword > SC > Treatment > treatment_key, values의 값
# 특정 Scenario, Scene, treatment_key에 해당하는 값을
# /raw/<int:scenario_num>/<int:sc_num>/<string:treatment_key>  # 모두 JSON으로 출력
# /html/<int:scenario_num>/<int:sc_num>/<string:treatment_key>  # 중복제거하여 HTML 템플릿으로 출력
# /json/<int:scenario_num>/<int:sc_num>/<string:treatment_key>  # 중복제거하여 JSON 데이터로 출력

# 사람이름 키워드를 받으면 그에 맞는 사람 정보를
api.add_resource(GetInfoPerson, '/<string:data_type>/<string:person_name>')
# /html/<string:person_name>    # HTMl 템플릿으로 출력
# /json/<string:person_name>    # JSON 데이터로 출력

# 특정 시간에 해당하는 데이터 출력
api.add_resource(LwMetadata, '/lw')

if __name__ == '__main__':
    # app.run(debug=True)        # 디버그 모드 실행
    app.run(host='0.0.0.0')  # 외부에서 접속가능한 서버로 실행
