import os
import json
from random import randint

from library.people_in_scene import data_split, data_rendering
from library.metadata_class import *
from library.read_srt import read_srt
from library.directory_control import get_file_dir_path, get_extended_path
from utils.video_control import get_sound_frame

null = None


def load_json(in_path):
    with open(in_path, 'rt', encoding="utf-8") as file:
        json_file = json.load(file)  # json -> dict

    return json_file


def save_json(result, out_path):
    with open(out_path, 'wt', encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)  # dict -> json


def get_opus_id(opus_name=None):
    """
            read "opus_id_list.txt" and
            return opus_id related to opus_name

            if there is no opus_name in "opus_id_list.txt",
            create opus_id and return it
    """
    assert opus_name is not None, "get_opus_id(): opus_name is required"
    opus_list_path = get_file_dir_path('opus_id_list.txt', 'metadata')
    with open(opus_list_path, 'rt') as f:
        opus_name_id_list = f.readlines()
        for opus_name_id in opus_name_id_list:
            opus_n, opus_id = opus_name_id.split()
            if opus_name == opus_n:
                return opus_id
        last_opus_name, last_opus_id = opus_name_id_list[-1].split()
        new_opus_id = str(int(last_opus_id) + 1)
        with open(opus_list_path, 'at') as f:
            f.write('\n{} {}'.format(opus_name, new_opus_id))

    return new_opus_id


class MetadataControl:
    class_data: Optional[Opus]

    def __init__(self, in_filepath: str = None, in_data: Union[dict, Opus] = None, out_filepath: str = None) -> None:
        """
        메타데이터를 임시저장, 완전저장 및 "메타데이터 입력기"에 필요한 데이터를 임시저장해주는 클래스
        MetadataControl Class offer following functions that
            temporarily or completely save Metadata and
            temporarily save any data needed from "Metadata Inputer"

        다음 조합의 parameter들을 필수로 입력 받아야함
        Following parameters must lifecycle
        [in_filepath] or [in_data, out_filepath]

        다음 parameter들의 조합이 가능함
        Following parameters are possible for lifecycle
        [in_filepath], [in_filepath, out_filepath],
        [in_data, out_filepath]

        :param in_filepath:
            읽어들일 JSON 데이터 파일경로
            JSON path to read Metadata
        :param in_data:
            저장할 dict or Opus 데이터
            dict() or Opus Class to save
        :param out_filepath:
            새로 저장할 JSON 파일명
            new JSON path to save dict()
        """
        assert in_filepath is not None or in_data is not None
        self.class_data = None
        self.cumulative_sum = list()
        self.sequence_scene_shot_struct = list()

        if in_filepath is not None:
            self.metadata_path = in_filepath
            self.load_json2class()
        elif in_data is not None:
            if isinstance(in_data, dict):
                self.class_data = self.dict2class(in_data)
            elif isinstance(in_data, Opus):
                self.class_data = in_data
            else:
                assert False, "Invalid parameter : in_data(dict, Opus)"
        else:
            assert False, "need one param, 'in_filepath or in_dict_data'"

        if out_filepath is not None:
            self.metadata_path = out_filepath
        self.save_class2json()
        print('Metadata Path : {}'.format(self.metadata_path))

    @classmethod
    def create_metadata_opus(cls, video_info: dict, out_path: str) -> 'MetadataControl':
        """
        :param video_info:
            입력할 영상의 기본적인 메타데이터 정보들
            basic metadata information of lifecycle video
                --> opus_kr_name, opus_name, season_num, episode_num
        :param out_path:
            최종적으로 저장하여 사용할 메타데이터 경로
            Metadata JSON path to save and use finally
        :return :
            MetadataControl Class
        """
        opus_kr_name = video_info['title_kor']
        opus_name = video_info['title_eng']

        new_opus_id = get_opus_id(opus_name)
        opus_class = Opus.from_dict(dict())
        opus_class.opus_id = new_opus_id
        opus_class.opus_name__kr = opus_kr_name
        opus_class.opus_name__en = opus_name

        metadata_control_ins = cls(in_data=opus_class, out_filepath=out_path)

        return metadata_control_ins

    def create_metadata_episode(self, video_info: dict) -> None:
        """
        front-end에서(유저로부터) 받은 비디오 메타데이터로 기본적인 episode 메타데이터 클래스 생성
        Create Episode Class based video metadata received from front-end(user)

        :param video_info:
            front-end에서(유저로부터) 받은 비디오 메타데이터
            video metadata received from front-end(user)
        """
        season_num = video_info['season']
        episode_num = video_info['episode']

        season_class_list = self.class_data.seasons
        curr_season_count = len(season_class_list)
        for i in range(curr_season_count, season_num):
            season_class_list.append(Season.from_dict(dict()))

        episode_class_list = season_class_list[season_num - 1].episodes
        curr_episode_count = len(episode_class_list)
        for i in range(curr_episode_count, episode_num):
            episode_class_list.append(Episode.from_dict(dict()))
        episode_class_list[episode_num - 1].fps = round(video_info['fps'], 2)

        sequence_class_list = episode_class_list[episode_num - 1].sequences
        sequence_class_list.append(Sequence.from_dict(dict()))
        sequence_class_list[0].scenes.append(Scene.from_dict(dict()))

    def update_preprocessed_data(self, video_data: dict, backup_path: str) -> None:
        """
        front-end에서 받은 비디오 전처리 결과로 전처리 데이터를 업데이트
        전처리 메타데이터를 저장한 초기 데이터는 백업함
        Update preprocessed data based video preprocess result received from front-end(user)
        initial data will be backup

        :param video_data:
            front-end에서 받은 비디오 메타데이터 중 전처리된 데이터
        :param backup_path:
            전처리 데이터를 저장한 초기 데이터를 백업할 경로
        """
        video_info = video_data['video_info']
        preprocess_data = video_data['data']

        season_num = video_info['season']
        episode_num = video_info['episode']

        for shot_data in preprocess_data:
            shot_start_frame = int(shot_data['start_frame'])
            shot_end_frame = int(shot_data['end_frame'])
            shot_keyframe_filename = shot_data['keyframe_path'].split('/')[-1]

            shot_class_ins = Shot.from_dict(dict())
            shot_class_ins.start_frame_num_episode = shot_start_frame
            shot_class_ins.end_frame_num_episode = shot_end_frame

            keyframe_ins = KeyframesNum.from_dict(dict())
            keyframe_ins.keyframe_num_episode = shot_start_frame
            keyframe_ins.keyframe_image_filename = shot_keyframe_filename
            shot_class_ins.keyframes_num.append(keyframe_ins)

            position_keys = list(['x', 'y', 'w', 'h'])
            for object_data in shot_data['objects']:
                person_ins = Person.from_dict(dict())
                positions_ins = Position.from_dict(dict())
                positions_ins.position_frame_num = shot_start_frame
                for key in position_keys:
                    positions_ins.position_xywh.append(float(object_data[key]))
                person_ins.positions.append(positions_ins)
                shot_class_ins.persons.append(person_ins)

            self.class_data.seasons[season_num - 1].episodes[episode_num - 1].sequences[0].scenes[0].shots.append(shot_class_ins)

        self.class_data.update_metadata()
        self.save_class2json(out_path=backup_path)
        self.save_class2json()

    @staticmethod
    def dict2class(dict_data: dict) -> Union[Opus, Season, Episode, Season, Scene, Shot]:
        """
            Metadata Class를 dict으로 변환
            class_from_dict 함수를 다른 python file에서 사용가능하도록 해줌
            Convert Metadata Class to dict()
            this function make class_from_dict() available to other python files

            ex)
                {episode_id: ...} -> Episode
                {season_id: ...} -> Season
        """
        data = class_from_dict(dict_data)  # dict -> class(object)

        return data

    def class2dict(self, class_data: Union[Opus, Season, Episode, Season, Scene, Shot, None] = None) -> dict:
        """
            self.class_data or class_data를 dict으로 변환
            Convert self.class_data or class_data to dict()

            ex)
                Episode -> {episode_id: ...}
                Season -> {season_id: ...}
        """
        if class_data is None:
            class_data = self.class_data
        data = class_to_dict(class_data)  # class(object) -> dict

        return data

    def load_json2class(self):
        """
            저장된 메타데이터 경로(self.metadata_path)의 JSON을 읽고 Class로 변환한 뒤,
            self.class_data로 저장
            After read JSON file from self.metadata_path and convert JSON to Class,
            save to self.class_data
        """
        json_file = load_json(self.metadata_path)
        self.class_data = self.dict2class(json_file)  # dict -> class(object)

    def save_class2json(self, out_path=None):
        """
            MetadataControl Class 내부에 저장된 Metadata Class 데이터를 JSON으로 저장
            Save Metadata Class data in "MetadataControl Class" to JSON
        """
        serial = self.class2dict()  # class(object) -> dict
        if out_path is None:
            out_path = self.metadata_path
        save_json(serial, out_path=out_path)

    def update_metadata_architecture(self, out_path=None):
        """
            JSON에서 읽은 메타데이터를 현재 수정된 구조로 업데이트 할 때 사용하는 함수
            현재는 사용하지 않음
            This function will use to update metadata read from JSON with the current modified metadata architecture
            no use currently
        """
        if out_path is None:
            out_path = get_extended_path(self.metadata_path, mid='.', extra='update')
        self.metadata_path = out_path
        self.save_class2json()

    def check_variable(self, data_type=None, params=None):
        """
            self.cumulative_sum과 self.sequence_scene_shot_struct가 초기화되어있는지 체크하여, 기본 값을 설정해주는 함수
            Checks whether
                self.cumulative_sum and self.sequence_scene_shot_struct are initialized and
                sets default values
        """
        if data_type == 'cumulative':
            data = self.cumulative_sum
        elif data_type == 'struct':
            data = self.sequence_scene_shot_struct
        else:
            assert False, 'data_type must be "cumulative" or "struct"'

        if params is not None:
            season_num, episode_num = params
        else:
            assert False, 'params must be [int, int]'

        total_season_num = len(data)
        for _ in range(total_season_num, season_num + 1):
            data.append(list())

        if episode_num == -1:
            episode_num = len(self.class_data.seasons[season_num].episodes)
        else:
            episode_num += 1
        total_episode_num = len(data[season_num])
        for i in range(total_episode_num, episode_num):
            data[season_num].append(list())

    def set_struct_data(self, data=None, params=None) -> Union[tuple, list]:
        """
            self.cumulative_sum으로 메타데이터의 구조에 대한 변수를 임시저장하는 함수
            Temporarily stores variables about the structure of metadata calculated from self.cumulative_sum
        """
        assert params is not None, 'Need params = [#, #], "params : {}"'.format(params)
        season_num, episode_num = params

        self.check_variable(data_type='struct', params=params)

        if data is None:
            reference_data = self.get_cumulative_sum(params=params)
            if isinstance(reference_data, list):
                pass
            else:
                return reference_data
            new_struct_data = list()
            start_shot_num = 0
            before_scene_len = 0
            for seq_data in reference_data:
                scene_len = int(list(seq_data.keys())[-1])
                for i in range(scene_len - before_scene_len):
                    if seq_data[scene_len][i] - start_shot_num == 0:
                        new_struct_data.append([0, 0])
                    else:
                        new_struct_data.append([start_shot_num + 1, seq_data[scene_len][i]])
                    start_shot_num = seq_data[scene_len][i]
                before_scene_len = scene_len
            self.sequence_scene_shot_struct[season_num][episode_num] = new_struct_data
        else:
            self.sequence_scene_shot_struct[season_num][episode_num] = data

        return self.sequence_scene_shot_struct[season_num][episode_num]

    def get_struct_data(self, params=None) -> Union[tuple, list]:
        """
            입력된 season, episode 번호에 맞는 메타데이터 구조 데이터를 return
            Return metadata structure data corresponding to the entered season and episode number
        """
        assert params is not None, 'Need params = [#, #], "params : {}"'.format(params)
        season_num, episode_num = params

        self.check_variable(data_type='struct', params=params)

        if len(self.sequence_scene_shot_struct[season_num][episode_num]) == 0:
            result = self.set_struct_data(params=params)
            if result:
                pass
            else:
                return result

        return self.sequence_scene_shot_struct[season_num][episode_num]

    def update_struct(self, params=None, data_type=None) -> None:
        """
            임시저장된 메타데이터 구조 데이터에 따라 self.class_data의 구조를 변환한 뒤, 메타데이터의 id들을 최신화
            Convert the structure of self.class_data according to the temporarily stored metadata structure data
            and then update the ids of the metadata.
        """
        assert params is not None, 'Need params = [#, #], "params : {}"'.format(params)
        season_num, episode_num = params
        if data_type in ['sequence', 'scene']:
            pass
        else:
            assert False, 'Need data_type = "sequence" or "scene", received : {}'.format(data_type)

        epi_data = self.dict2class(self.get_data(params=params))
        origin_scene_list: List[Scene] = list()
        new_list: List[List[Scene]] = list()

        if data_type == 'sequence':
            for seq_data in epi_data.sequences:
                origin_scene_list += seq_data.scenes

            for scene_data in origin_scene_list:
                if len(new_list) == 0 or new_list[-1][-1].sequence_title != scene_data.sequence_title:
                    new_list.append([scene_data])
                else:
                    new_list[-1].append(scene_data)

            curr_sequences = self.class_data.seasons[season_num].episodes[episode_num].sequences
            for new_seq_idx, new_scene_list in enumerate(new_list):
                if len(curr_sequences) == new_seq_idx:
                    curr_sequences += [Sequence.from_dict(dict())]
                curr_sequences[new_seq_idx].scenes = new_scene_list
                if len(new_scene_list) != 0:
                    curr_sequences[new_seq_idx].sequence_title = new_scene_list[0].sequence_title

            self.class_data.seasons[season_num].episodes[episode_num].sequences = curr_sequences[:len(new_list)]

        else:
            struct_data = self.get_struct_data(params=params)
            for seq_data in epi_data.sequences:
                for scene_data in seq_data.scenes:
                    origin_scene_list += scene_data.shots

            for seq_idx in range(len(epi_data.sequences)):
                new_list.append(list())
                for start, end in struct_data:
                    if start == end == 0:
                        new_list[-1].append(list())
                    else:
                        new_list[-1].append(origin_scene_list[start - 1: end])

            curr_sequences = self.class_data.seasons[season_num].episodes[episode_num].sequences
            for seq_idx, new_scene_list in enumerate(new_list):
                curr_scenes = self.class_data.seasons[season_num].episodes[episode_num].sequences[seq_idx].scenes
                for scene_idx, shot_list in enumerate(new_scene_list):
                    if len(curr_scenes) == scene_idx:
                        curr_scenes += [Scene.from_dict(dict())]
                    curr_scenes[scene_idx].shots = shot_list
                self.class_data.seasons[season_num].episodes[episode_num].sequences[seq_idx].scenes = \
                    curr_scenes[:len(new_scene_list)]
            self.class_data.seasons[season_num].episodes[episode_num].sequences = curr_sequences[:len(new_list)]

        self.set_struct_data(params=params)
        self.set_cumulative_sum(params=params)

        self.class_data.seasons[season_num].episodes[episode_num].update_episode_data()

    def set_cumulative_sum(self, params=None):
        """
            현재 저장된 self.class_data의 scene, shot 누적합을 계산하여 임시저장
            episode가 -1(front-end에서는 0으로 넘김)일 경우, 모든 episode의 누적합을 계산
            Calculate the cumulative sum of scene and shot of currently stored self.class_data and temporarily save
            If episode is -1 (zero in front-end), calculate the cumulative sum of all episodes.
        """
        assert self.class_data is not None, "Error : You should execute 'load_json2class()'"
        result = self.get_data(params=params)
        if isinstance(result, dict):
            pass
        else:
            return result
        season_num, episode_num = params

        if episode_num == -1:
            total_episode_num_per_season = len(self.class_data.seasons[season_num].episodes)
            for episode_num in range(total_episode_num_per_season):
                self.set_cumulative_sum_per_episode(season_num, episode_num)
        else:
            self.set_cumulative_sum_per_episode(season_num, episode_num)

    def set_cumulative_sum_per_episode(self, season_num, episode_num):
        """
            특정 episode의 scene, shot 누적합을 계산
            Calculate the cumulative sum of scene and shot of a specific episode
        """
        epi_data = self.class_data.seasons[season_num].episodes[episode_num]
        cumulative_scene = 0
        cumulative_shot = 0
        self.cumulative_sum[season_num][episode_num] = list()
        for seq in epi_data.sequences:
            cumulative_scene += len(seq.scenes)
            self.cumulative_sum[season_num][episode_num] += [{cumulative_scene: list()}]
            for sc in seq.scenes:
                cumulative_shot += len(sc.shots)
                self.cumulative_sum[season_num][episode_num][-1][cumulative_scene].append(cumulative_shot)

    def get_cumulative_sum(self, params=None):
        """
            특정 season, episode의 누적합을 반환
            episode가 -1(front-end에서는 0으로 넘김)일 경우, 모든 episode의 누적합을 반환
            Return cumulative sum of a certain season and episode
            If episode is -1 (zero in front-end), cumulative sum of all episodes is returned.
        """
        if params is None:
            season_num, episode_num = params = [0, 0]
        else:
            season_num, episode_num = params

        self.check_variable(data_type='cumulative', params=params)
        result = self.get_data(params=params)
        if isinstance(result, dict):
            pass
        else:
            return result

        if episode_num == -1:
            total_episode_num_per_season = len(self.class_data.seasons[season_num].episodes)
            for episode_num in range(total_episode_num_per_season):
                if len(self.cumulative_sum[season_num][episode_num]) == 0:
                    self.set_cumulative_sum_per_episode(season_num, episode_num)
            return self.cumulative_sum[season_num]
        else:
            if len(self.cumulative_sum[season_num][episode_num]) == 0:
                self.set_cumulative_sum(params=params)

            return self.cumulative_sum[season_num][episode_num]

    def set_data(self, data=None, params=None):
        """
            Episode, Scene, Shot 중 하나의 데이터를 받아서 현재 저장된 self.class_data를 수정하는 함수
            Receives one of Episode, Scene and Shot data and modifies currently stored self.class_data
        """
        if isinstance(data, dict):
            pass
        else:
            print('data : {}'.format(data))
            assert False, 'required type: dict()'

        result = self.get_data(params=params)
        if isinstance(result, dict):
            pass
        else:
            return result

        for key in data.keys():
            if key in result.keys():
                result[key] = data[key]
            else:
                assert False, 'incorrect keys : \n' \
                              'received keys : "{}",' \
                              'expected keys list : "{}"'.format(data.keys(), result.keys())
        class_data = self.dict2class(result)

        if len(params) == 3:
            season_num, episode_num = params
            self.class_data.seasons[season_num].episodes[episode_num] = class_data
        elif len(params) == 4:
            season_num, episode_num, sequence_num, scene_num = params
            self.class_data.seasons[season_num].episodes[episode_num].sequences[sequence_num].scenes[
                scene_num] = class_data
        else:
            season_num, episode_num, sequence_num, scene_num, shot_num = params
            self.class_data.seasons[season_num].episodes[episode_num].sequences[sequence_num].scenes[
                scene_num].shots[shot_num] = class_data

        return result

    def get_data(self, params=None):
        """
            임시저장된 메타데이터에서 원하는 부분을 반환해주는 함수
            Returns the desired part of the temporarily stored metadata
        """
        assert params is not None, 'need params as list() : HTTP get parameter'
        class_list = ['seasons', 'episodes', 'sequences', 'scenes', 'shots']
        class_list = class_list[:len(params)]
        dict_data = self.class2dict()
        param_str = str()
        index_str = str()
        for i, class_names in enumerate(class_list):
            class_length = len(dict_data[class_names])
            if class_length > params[i]:
                dict_data = dict_data[class_names][params[i]]
                param_str += '{}({}), '.format(class_list[i], params[i] + 1)
                index_str += '{}({}), '.format(class_list[i], params[i] + 1)
            else:
                param_str += '{}({})'.format(class_list[i], params[i] + 1)
                index_str += '{}(<= {}),'.format(class_list[i], class_length)
                return param_str, index_str

        return dict_data

    # 이하는 lifeCycle_api.py에 사용되었던 부분
    # The following part was used in lifeCycle_api.py
    def set_random_conflict_avg(self):
        result = set_random_conflict_avg(self.class_data)
        result = self.class2dict(result)
        out_path = get_extended_path(self.metadata_path, mid='.', extra='random_conflict_avg')
        save_json(result, out_path=out_path)

    def add_one_type_metadata(self, typeValue):
        # typeValue : (1: action, 2: face, 3: sound, 4: script)
        result, extra_name = set_type_metadata(self.class_data, value=typeValue)
        result = self.class2dict(result)
        out_path = get_extended_path(self.metadata_path, mid='_', extra=extra_name)
        save_json(result, out_path=out_path)

    def sum_metadata(self, metadata_file_name_list=None):
        self.class_data = sum_metadata(self.class_data, metadata_file_name_list)
        self.metadata_path = get_extended_path(self.metadata_path, mid='_', extra='sum')
        self.save_class2json()

    def get_life_cycle(self):
        scenes, scene_count = data_split(self.class_data)  # class로된 데이터 쪼개서 Episode별 Scene 객체들로 저장
        life_cycle_data = data_rendering(scenes, scene_count)  # Scene안의 plot에서 인물등장횟수를 Scene별로 체크하여 저장

        out_path = get_extended_path(self.metadata_path, mid='.', extra='lifeCycle')
        save_json(life_cycle_data, out_path=out_path)  # 인물 라이프 사이클 데이터를 파일 출력

        return life_cycle_data


# deserial : 기존에 있는 json(원본)을 Class로 변환한 객체
# result : scene, shot 단위 평균 갈등값을 1~5사이 랜덤한 float으로 설정된 Class 객체
def set_random_conflict_avg(deserial):
    # shot, scene의 갈등 점수를 1~5사이 float값을 초기값 set
    # 계층구조 : opus > seasons > episodes > sequences > scenes > shots
    # seasons는 무조건 1개, episodes는 총 11개있음.

    result = deserial
    # 11개 에피소드 순환
    for e, episode in enumerate(deserial.seasons[0].episodes):
        # 각 에피소드 내의 sequence 배열 순환
        for s, sequence in enumerate(episode.sequences):
            # 각 sequence 내에 scene 배열 순환
            for sc, scene in enumerate(sequence.scenes):
                # 매번 random값 설정
                rand_float = float(randint(10, 50)) / 10
                result.seasons[0].episodes[e].sequences[s].scenes[sc].scene_conflict_avg = rand_float

                # 각 scene 내에 shot 배열 순환
                for sh, shot in enumerate(scene.shots):
                    rand_float = float(randint(10, 50)) / 10
                    result.seasons[0].episodes[e].sequences[s].scenes[sc].shots[sh].shot_conflict_avg = rand_float
    return result


# 4가지 type에 따른 metadata 입력함수
# deserial : 기존에 있는 json(원본)을 Class로 변환한 객체
# result : scene, shot 단위 평균 갈등값을 1~5사이 랜덤한 float으로 설정된 Class 객체
# typeValue : (1: action, 2: face, 3: sound, 4: script)
def set_type_metadata(deserial, value=1):
    # 계층구조 : opus > seasons > episodes > sequences > scenes > shots
    # seasons는 무조건 1개, episodes는 총 11개있음.

    type_dict = {1: "action", 2: "face", 3: "sound", 4: "script"}
    result = deserial
    if value == 1:
        # action metadata set
        for e, episode in enumerate(deserial.seasons[0].episodes):
            # 각 에피소드 내의 sequence 배열 순환
            for s, sequence in enumerate(episode.sequences):
                # 각 sequence 내에 scene 배열 순환
                for sc, scene in enumerate(sequence.scenes):
                    # 각 scene 내에 shot 배열 순환
                    for sh, shot in enumerate(scene.shots):
                        # 각 shot내에 keyframes_num 배열 순환
                        for k, keyframe in enumerate(shot.keyframes_num):
                            # shot.keyframes_num[].keyframe_action = (str)
                            # shot.keyframes_num[].keyframe_action_conflict = (1,2,3,4,5)
                            # 아래에서 사용한 변수는 예시
                            result.seasons[0].episodes[e].sequences[s].scenes[sc].shots[sh].keyframes_num[
                                k].keyframe_action = 'example'
                            result.seasons[0].episodes[e].sequences[s].scenes[sc].shots[sh].keyframes_num[
                                k].keyframe_action_conflict = 1
    elif value == 2:
        # face metadata set
        for e, episode in enumerate(deserial.seasons[0].episodes):
            # 각 에피소드 내의 sequence 배열 순환
            for s, sequence in enumerate(episode.sequences):
                # 각 sequence 내에 scene 배열 순환
                for sc, scene in enumerate(sequence.scenes):
                    # 각 scene 내에 shot 배열 순환
                    for sh, shot in enumerate(scene.shots):
                        # 각 shot내에 faces변수에 Face 좌표리스트 삽입
                        face_list = list()
                        # face_number : 각 shot에 나오는 face 좌표집단의 갯수 / 여기에는 예시로 3
                        face_number = 3
                        for i in range(face_number):
                            # face_frame_num = (int)
                            # face_time = (str)
                            # face_xywh = list(float)
                            # face_name = (str)
                            # face_emotion = list(float)
                            instance_face = Face(face_frame_num=1,
                                                 face_time='00:00:00.000',
                                                 face_xywh=[1.1, 1.2, 20.0, 30.0],
                                                 face_name='example_name',
                                                 face_emotion=[0.1, 0.5, 0.52, 0.3, 0.221, 0.12, 0.91],
                                                 face_actor_name='',
                                                 face_expression='',
                                                 face_intensity=2.5)
                            face_list.append(instance_face)
                        result.seasons[0].episodes[e].sequences[s].scenes[sc].shots[sh].faces = face_list.copy()
    elif value == 3:
        srt_filename = ['misaeng.S1.E0001_2.srt']
        srt_file_path = get_file_dir_path(srt_filename, ['metadata', 'lifecycle'])
        srt_data = read_srt(srt_file_path)
        srt_index = 0

        # sound metadata set
        for e, episode in enumerate(deserial.seasons[0].episodes):
            if e >= 1:
                break
            # 각 에피소드 내의 sequence 배열 순환
            for s, sequence in enumerate(episode.sequences):
                # 각 sequence 내에 scene 배열 순환
                for sc, scene in enumerate(sequence.scenes):
                    # 각 scene 내에 shot 배열 순환
                    for sh, shot in enumerate(scene.shots):
                        # 각 shot내에 sounds변수에 Face 좌표리스트 삽입
                        sound_list = list()
                        while True:
                            # print(srtData[srtindex][0], shot.start_time_episode)
                            if srt_data[srt_index][0] < shot.start_time_episode:
                                pass
                            elif shot.start_time_episode <= srt_data[srt_index][0] <= shot.end_time_episode:
                                # sound_time = (str)
                                # sound_frame_num = (str) / 소수점 2자리
                                # sound_conflict = (float)
                                sound_time = srt_data[srt_index][0]
                                sound_frame_num = get_sound_frame(sound_time)
                                sound_conflict_value = round((float(srt_data[srt_index][1]) - 0.5) * 10.0, 3)
                                instance_sound = Sound(sound_time=sound_time,
                                                       sound_frame_num=sound_frame_num,
                                                       sound_conflict=sound_conflict_value)
                                sound_list.append(instance_sound)
                            else:
                                break
                            srt_index += 1
                        result.seasons[0].episodes[e].sequences[s].scenes[sc].shots[sh].sounds = sound_list
    elif value == 4:
        # script metadata set
        for e, episode in enumerate(deserial.seasons[0].episodes):
            # 각 에피소드 내의 sequence 배열 순환
            for s, sequence in enumerate(episode.sequences):
                # 각 sequence 내에 scene 배열 순환
                for sc, scene in enumerate(sequence.scenes):
                    # scenes[].script_scene_conflict = (float)
                    # 아래에서 사용한 값은 예시
                    result.seasons[0].episodes[e].sequences[s].scenes[sc].script_scene_conflict = 1.0
    else:
        print("value range : (1~4)")
        raise ValueError

    return result, type_dict[value]


# 각 json 파일에서 데이터 받아서 합침
# scene_conflict_avg, shot_conflict_avg 계산
def set_conflict_avg(obj, keyframes_num=null, faces=null, sounds=null, script_scene_conflict=null):
    print("set_conflict_avg start")
    print(keyframes_num, faces, sounds, script_scene_conflict)
    emotion_default = [[-4, 3],
                       [-4, 1],
                       [-3, 4],
                       [4, 1],
                       [3, -3],
                       [2, -4],
                       [2, 4]]
    if type(obj) is Shot:
        if keyframes_num != null and faces != null and sounds != null:
            obj.keyframes_num = keyframes_num
            obj.faces = faces
            obj.sounds = sounds

            keyframe_avg, face_avg, sound_avg = 0, [0, 0], 0
            if len(keyframes_num) != 0:
                for keyframe in keyframes_num:
                    keyframe_avg += keyframe.keyframe_action_conflict
                keyframe_avg /= len(keyframes_num)

            if len(faces) != 0:
                for face in faces:
                    for emotion_idx, face_emotion in enumerate(face.face_emotion):
                        for idx in range(2):
                            face_avg[idx] += face_emotion * emotion_default[emotion_idx][idx]
                face_avg[0] /= 7 * len(faces)
                face_avg[1] /= 7 * len(faces)

            if len(sounds) != 0:
                for sound in sounds:
                    sound_avg += sound.sound_conflict
                sound_avg /= len(sounds)

            obj.shot_conflict_avg = [face_avg[0], (face_avg[1] + keyframe_avg + sound_avg) / 3]
        else:
            print("invalid data")
            raise ValueError

    elif type(obj) is Scene:
        shot_avg = [0, 0]
        if len(obj.shots) != 0:
            for shot in obj.shots:
                for idx in range(2):
                    shot_avg[idx] += shot.shot_conflict_avg[idx]
            shot_avg[0] /= len(obj.shots)
            shot_avg[1] /= len(obj.shots)

        if script_scene_conflict == null:
            script_scene_conflict = 0
        obj.script_scene_conflict = script_scene_conflict
        obj.scene_conflict_avg = [(shot_avg[0] + script_scene_conflict) / 2, shot_avg[1]]

    else:
        print("invalid obj")
        raise ValueError
    return obj


def sum_metadata(result, file_name_list=None):
    # 합칠 json 파일들
    if file_name_list is None:
        file_name_list = ["1001_v1_face.json", "1001_v1_action.json", "1001_v1_script.json", "1001_v3_sound.json"]
    file_dir_list = get_file_dir_path(file_name_list, ['metadata', 'lifecycle'])
    opus_obj_list = list()

    for file_dir in file_dir_list:
        file = open(file_dir, 'rt', encoding='UTF8')
        json_file = json.load(file)
        opus_obj_list.append(class_from_dict(json_file))
    print(opus_obj_list)
    print("finishing load json")
    face_data, action_data, script_data, sound_data = opus_obj_list

    for e, episode in enumerate(result.seasons[0].episodes):
        if e >= 1:
            break
        # 각 에피소드 내의 sequence 배열 순환
        for s, sequence in enumerate(episode.sequences):
            # 각 sequence 내에 scene 배열 순환
            for sc, scene in enumerate(sequence.scenes):
                print("scene # : ", sc)
                # 각 scene 내에 shot 배열 순환
                for sh, shot in enumerate(scene.shots):
                    print("shot # : ", sh)
                    result.seasons[0].episodes[e].sequences[s].scenes[sc].shots[sh] = \
                        set_conflict_avg(result.seasons[0].episodes[e].sequences[s].scenes[sc].shots[sh],
                                         keyframes_num=action_data.seasons[0].episodes[e].sequences[s].scenes[sc].shots[
                                             sh].keyframes_num,
                                         faces=face_data.seasons[0].episodes[e].sequences[s].scenes[sc].shots[sh].faces,
                                         sounds=sound_data.seasons[0].episodes[e].sequences[s].scenes[sc].shots[
                                             sh].sounds)
                print("end shot")
                result.seasons[0].episodes[e].sequences[s].scenes[sc] = \
                    set_conflict_avg(result.seasons[0].episodes[e].sequences[s].scenes[sc],
                                     script_scene_conflict=script_data.seasons[0].episodes[e].sequences[s].scenes[
                                         sc].script_scene_conflict)
            print("end scene")

    return result
