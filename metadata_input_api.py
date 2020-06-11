"""
Description
    Functions to search/modify/save desired metadata about video
"""

from flask import Flask, make_response, request
from flask_restful import Resource, Api
from library.directory_control import get_file_dir_path
from utils.metadata_control import MetadataControl
from utils.time_control import TimeControl
from flask_cors import CORS

import os
import json
from typing import Union, Tuple, List

app = Flask(__name__)
api = Api(app)

# solve cross-origin error
# IP addr : another flask-server to communicate
cors = CORS(app, resources={r"/*": {"origins": "IP addr"}})

# Metadata variable
metadata = dict()


def get_description():
    dict_data = dict()
    dict_data['/preprocess/json'] = '전처리 데이터를 저장하는 API'
    dict_data['/opus/struct/json?season=a & episode=b & save=False'] =\
        'season = a, episode = b인 메타데이터 구조화 정보를 반환<br>' \
        'save = 완전 저장 여부'
    dict_data['/opus/all/json'] = 'opus 단위의 전체 메타데이터를 반환'
    dict_data['/opus/episode/json?season=a & episode=b & save=False & no_full=False'] =\
        'episode 단위로 메타데이터를 반환하는 기능<br>' \
        'save = 완전 저장 여부<br>' \
        'no_full=False : episode 전체 반환'
    dict_data['/opus/scene/json?season=a & episode=b & sequence=c & scene=d & save=False'] =\
        'scene 단위로 메타데이터를 반환하는 기능<br>' \
        'save = 완전 저장 여부'
    dict_data['/opus/shot/json?season=a & episode=b & sequence=c & scene=d & shot=e & save=False'] =\
        'shot 단위로 메타데이터를 반환하는 기능<br>' \
        'save = 완전 저장 여부'
    dict_data['/opus/total_num?season=a & episode=b'] = 'Scene, Shot 누적합을 반환' \
                                                        'if episode != 0: season = a, episode = b인 누적합을 반환' \
                                                        'if episode == 0: season = a인 누적합 정보를 모두 반환하는 기능'

    api_error_msg = '<h2>Metadata Input RESTful API List</h2>'
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


class ApiDescription(Resource):
    def get(self):
        api_description = get_description()

        res = make_response(api_description)
        res.headers['Content-type'] = 'text/html; charset=utf-8'
        return res


def get_param_parsing(param_type: str) -> Tuple[List[int], bool, bool]:
    """
        HTTP GET 방식으로 받은 파라미터를 받아서 그 결과를 return
        Receive the parameter from HTTP GET method and return the result
    """
    param_list = ['season', 'episode', 'sequence', 'scene', 'shot', 'save', 'no_full']
    assert param_type in param_list
    value_list = list()
    args = request.args
    for param_name in param_list:
        if param_name not in ['save', 'no_full']:
            value_list.append(args.get(param_name, default=1, type=int) - 1)
        else:
            value_list.append(args.get(param_name, default=False, type=bool))

    return_start = param_list.index(param_type) + 1
    is_save = value_list[-2]
    no_full = value_list[-1]

    return value_list[:return_start], is_save, no_full


def get_metadata_control(opus: str = None, video_data: dict = None) -> MetadataControl:
    """
        'opus' or 'video_data' is required
        Function that return MetadataControl Class for managing "opus" metadata

        :param opus:            opus english name
        :param video_data:      video basic information and preprocessed data for generating metadata
        :return:                MetadataControl Class
    """
    video_info = None
    if opus is not None:
        pass
    elif video_data is not None:
        video_info = video_data['video_info']
        opus = video_info['title_eng']
    else:
        assert False, "need 'opus' or 'video_info' parameter"

    new_file = opus + '.json'
    origin_file = opus + '.origin.json'
    opus_path = get_file_dir_path(new_file, dir_route=['metadata', 'lifecycle', opus])
    origin_path = get_file_dir_path(origin_file, dir_route=['metadata', 'lifecycle', opus])

    if opus not in metadata.keys() or metadata[opus] is None:
        print('There is no opus data : {}\n'
              'Now read {}'.format(opus, new_file))
        if os.path.exists(opus_path):
            metadata[opus] = MetadataControl(in_filepath=opus_path, out_filepath=opus_path)
        else:
            print('There is no file : {}\n'
                  'Now create new {} from {}'.format(opus_path, new_file, origin_file))
            if os.path.exists(origin_path):
                metadata[opus] = MetadataControl(in_filepath=origin_path, out_filepath=opus_path)
            else:
                print('There is no file : {}\n'
                      'Now create new {}'.format(origin_path, new_file))
                if video_info is not None:
                    metadata[opus] = MetadataControl.create_metadata_opus(video_info=video_info, out_path=opus_path)
                else:
                    assert False, 'Cannot create {}.\n' \
                                  'Please lifecycle value : "video_info"'.format(new_file)

    if video_info is not None:
        metadata[opus].create_metadata_episode(video_info)
        metadata[opus].update_preprocessed_data(video_data=video_data, backup_path=origin_path)

    return metadata[opus]


def get_err_msg(result: tuple) -> dict:
    """
        에러메세지를 tuple(str, str)로 받아 dict으로 return 해주는 함수
        Function that receives error message as tuple(str, str) and returns to dict()
    """
    param_str, index_str = result
    err_msg = dict()
    err_msg['Received Index'] = param_str
    err_msg['Possible Index'] = index_str

    return {'Error': err_msg}


def get_response_dict(data: Union[list, dict, tuple] = None, timer_log: dict = None) -> dict:
    """
        각 API에서 처리된 데이터를 response용 dict으로 변환시키는 함수
        A function that converts data processed by each API to dict() for response.

        :param data:
            list: ?
            dict: ?
            tuple: error message
        :param timer_log:
            API 함수에서 실행된 동작시간을 저장한 변수
            Variables that store operating time executed in API function
    """
    assert isinstance(data, (list, dict, tuple)) and isinstance(timer_log, dict)

    response_dict = dict()
    response_dict['status'] = None
    response_dict['timer'] = timer_log
    if isinstance(data, tuple):
        response_dict['status'] = 'fail'
        response_dict['data'] = get_err_msg(data)
    else:
        response_dict['status'] = 'success'
        response_dict['data'] = data

    return response_dict


class Preprocess(Resource):
    """
        전처리된 데이터를 받아서 해당하는 영상의 메타데이터에 저장하는 API
        API that receives preprocessed data and stores it in the metadata of the corresponding video.
    """
    response_dict = dict()

    def post(self):
        time_control = TimeControl()
        timer_log = dict()

        video_data = request.get_json()
        video_data['video_info']['season'] = int(video_data['video_info']['season'])
        video_data['video_info']['episode'] = int(video_data['video_info']['episode'])

        time_control.timer_start()
        _ = get_metadata_control(video_data=video_data)
        timer_log['get_metadata_control'] = time_control.timer_end()

        self.response_dict = get_response_dict(data=video_data['video_info'], timer_log=timer_log)
        res = make_response(json.dumps(self.response_dict, indent=2, ensure_ascii=False))
        res.headers['Content-type'] = 'application/json'
        return res


class Struct(Resource):
    """
        메타데이터의 구조 정보를 읽거나, 수정, 저장하는 API
        API that read, modify, and save the structure information of metadata

        GET Method:     현재의 메타데이터 구조 정보를 반환
                        Return information of the current metadata structure
        POST Method:    Front-end에서 수정한 구조를 임시저장, 완전저장
                        Temporarily save or completely save the structure modified in the front-end
            임시저장:   수정한 변수값만 MetadataControl 클래스에 저장
            완전저장:   Front-end에서 요청한 구조대로 self.class_data의 구조를 변환하고, JSON에 백업
            Temporarily save:   Save only modified variable values to MetadataControl class
            Completely Save: Convert the structure of self.class_data to the structure requested by the front-end and back it up to JSON
    """
    response_dict = dict()

    def get(self, opus):
        time_control = TimeControl()
        timer_log = dict()

        params, _, __ = get_param_parsing(param_type='episode')
        metadata_control_ins = get_metadata_control(opus)

        time_control.timer_start()
        struct_data = metadata_control_ins.get_struct_data(params=params)
        timer_log['get_struct_data'] = time_control.timer_end()

        self.response_dict = get_response_dict(data=struct_data, timer_log=timer_log)
        print(self.response_dict)

        res = make_response(json.dumps(self.response_dict['data'], indent=2, ensure_ascii=False))
        res.headers['Content-type'] = 'application/json'
        return res

    def post(self, opus):
        time_control = TimeControl()
        timer_log = dict()

        params, is_save, _ = get_param_parsing(param_type='episode')
        metadata_control_ins = get_metadata_control(opus)
        struct_list = request.get_json()

        time_control.timer_start()
        result = metadata_control_ins.set_struct_data(data=struct_list, params=params)
        timer_log['set_struct_data'] = time_control.timer_log()
        if isinstance(result, tuple):
            pass
        else:
            if is_save:
                metadata_control_ins.update_struct(params=params, data_type='scene')
                timer_log['update_struct'] = time_control.timer_log()

                metadata_control_ins.save_class2json()
                timer_log['save_class2json'] = time_control.timer_log()

        self.response_dict = get_response_dict(data=result, timer_log=timer_log)
        res = make_response(json.dumps(self.response_dict, indent=2, ensure_ascii=False))
        res.headers['Content-type'] = 'application/json'
        return res


class MetadataControlAPI(Resource):
    """
        메타데이터를 검색, 수정, 저장하는 API
        API to retrieve, modify, and save metadata

        GET Method:     params에 맞는 메타데이터를 반환
                        Return information of the current metadata structure
        POST Method:    Front-end에서 수정한 메타데이터를 임시 혹은 완전 저장
                        Temporarily or completely save metadata modified by the front-end
            임시저장:   수정한 메타데이터를 MetadataControl 클래스에 저장
            완전저장:   Front-end에서 수정한 메타데이터로 JSON에 백업
            Temporarily save:   Save the modified metadata to the MetadataControl class
            Completely Save:    Back up to JSON with metadata modified by front-end
    """
    response_dict = dict()

    def get(self, opus, class_type):
        # params, is_save = get_param_parsing(param_type='episode')
        # metadata_control_ins = get_metadata_control(opus)
        #
        # result = metadata_control_ins.get_data(params=params)
        # if isinstance(result, tuple):
        #     param_str, index_str = result
        #     err_msg = dict()
        #     err_msg['Received Index'] = param_str
        #     err_msg['Possible Index'] = index_str
        #     dict_data = {'Error': err_msg}
        # else:
        #     dict_data = result
        #
        # res = make_response(json.dumps(dict_data, indent=2, ensure_ascii=False))
        # res.headers['Content-type'] = 'application/json'
        # return res
        time_control = TimeControl()
        timer_log = dict()

        if class_type == 'all':
            time_control.timer_start()
            metadata_control_ins = get_metadata_control(opus)
            timer_log['get_metadata_control'] = time_control.timer_log()
            result = metadata_control_ins.class2dict()
            timer_log['class2dict'] = time_control.timer_end()
        else:
            params, _, no_full = get_param_parsing(param_type=class_type)
            metadata_control_ins = get_metadata_control(opus)

            time_control.timer_start()
            result = metadata_control_ins.get_data(params=params)
            timer_log['get_data'] = time_control.timer_end()
            if isinstance(result, tuple):
                pass
            else:
                if class_type == 'episode':
                    if no_full:
                        del result['sequences']
                if class_type == 'scene':
                    del result['shots']

        self.response_dict = get_response_dict(data=result, timer_log=timer_log)
        print_dict = dict()
        for key in self.response_dict.keys():
            if key != 'data':
                print_dict[key] = self.response_dict[key]
        print(print_dict)
        print('{"data"}:', self.response_dict['data'])

        res = make_response(json.dumps(self.response_dict['data'], indent=2, ensure_ascii=False))
        res.headers['Content-type'] = 'application/json'
        return res

    def post(self, opus, class_type):
        # params, is_save = get_param_parsing(param_type='episode')
        # metadata_control_ins = get_metadata_control(opus)
        # episode_dict_data = request.get_json()
        #
        # metadata_control_ins.set_data(data=episode_dict_data, params=params, is_save=is_save)
        #
        # res = make_response(json.dumps(episode_dict_data, indent=2, ensure_ascii=False))
        # res.headers['Content-type'] = 'application/json'
        # return res
        time_control = TimeControl()
        timer_log = dict()

        params, is_save, _ = get_param_parsing(param_type=class_type)
        metadata_control_ins = get_metadata_control(opus)
        dict_data = request.get_json()

        time_control.timer_start()
        result = metadata_control_ins.set_data(data=dict_data, params=params)
        timer_log['set_data'] = time_control.timer_log()
        if isinstance(result, tuple):
            pass
        else:
            if is_save:
                if len(params) == 4:
                    metadata_control_ins.update_struct(params=params[:2], data_type='sequence')
                    timer_log['update_struct'] = time_control.timer_log()

                metadata_control_ins.save_class2json()
                timer_log['save_class2json'] = time_control.timer_log()

                result = metadata_control_ins.get_cumulative_sum(params=params[:2])

        self.response_dict = get_response_dict(data=result, timer_log=timer_log)

        res = make_response(json.dumps(self.response_dict, indent=2, ensure_ascii=False))
        res.headers['Content-type'] = 'application/json'
        return res


class TotalSceneShotNum(Resource):
    """
        특정 Episode에 대해 Scene 누적합 및 Shot 누적합을 반환하는 API
        APIs that return Scene Cumulative Sum and Shot Cumulative Sum for a specific Episode
    """
    response_dict = dict()

    def get(self, opus):
        time_control = TimeControl()
        timer_log = dict()

        params, _, __ = get_param_parsing(param_type='episode')
        metadata_control_ins = get_metadata_control(opus)

        time_control.timer_start()
        result = metadata_control_ins.get_cumulative_sum(params)
        timer_log['get_cumulative_sum'] = time_control.timer_end()

        self.response_dict = get_response_dict(data=result, timer_log=timer_log)
        print(self.response_dict)

        res = make_response(json.dumps(self.response_dict['data'], indent=2, ensure_ascii=False))
        res.headers['Content-type'] = 'application/json'
        return res


# API들을 설명하는 API
api.add_resource(ApiDescription, '/')
# 전처리 데이터를 저장하는 API
# API to store preprocessing data
api.add_resource(Preprocess, '/preprocess/json')
# 메타데이터 구조 정보를 제어하는 API
# API to control metadata structure information
api.add_resource(Struct, '/<string:opus>/struct/json')
# 메타데이터를 제어하는 API
# API to control metadata
api.add_resource(MetadataControlAPI, '/<string:opus>/<string:class_type>/json')
# Scene, Shot 누적합을 return하는 API
# API to return scene and shot cumulative sum
api.add_resource(TotalSceneShotNum, '/<string:opus>/total_num')


if __name__ == '__main__':
    opus_list_path = get_file_dir_path('opus_id_list.txt', ['metadata', 'lifecycle'])
    with open(opus_list_path, 'wt+') as f:
        opus_name_id_list = f.readlines()
        for line in opus_name_id_list:
            opus_name, _ = line.split()
            metadata[opus_name] = get_metadata_control(opus_name)
    # app.run(debug=True, host='0.0.0.0', port='15000')        # 디버그 모드 실행
    app.run(host='0.0.0.0', port='15000')  # 외부에서 접속가능한 서버로 실행
