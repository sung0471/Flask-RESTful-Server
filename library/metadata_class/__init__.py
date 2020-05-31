from library.metadata_class.convert_type import *
from library.metadata_class.opus import *
from library.metadata_class.episode import *
from library.metadata_class.sequence import *
from library.metadata_class.scene import *
from library.metadata_class.shot import *


def class_from_dict(s: dict) -> Union[Opus, Season, Episode, Season, Scene, Shot]:
    """
    :param s: dict of Metadata
    :return : Class of Metadata

    무슨 메타데이터 타입인지 체크하여 dict을 Class로 변환
    check dictionary what Metadata type is and convert to Metadata Class
    """
    type_list = ['seasons', 'episodes', 'sequences', 'scenes', 'shots', 'persons']
    class_list = [Opus, Season, Episode, Sequence, Scene, Shot]
    for i, key_type in enumerate(type_list):
        if key_type in s.keys():
            return class_list[i].from_dict(s)


def class_to_dict(x: Any) -> dict:
    """
    :param x: Class of Metadata
    :return : dict

    convert Class to dict
    """
    type_list = [Opus, Season, Episode, Sequence, Scene, Shot]
    for class_type in type_list:
        if isinstance(x, class_type):
            return to_class(class_type, x)


if __name__ == '__main__':
    import json
    import os
    json_dir = 'json/'
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    # get metadata class
    # 1. use_misaeng = True
    #   read "misaeng.json"
    # 2. use_misaeng = False
    #   create empty metadata
    use_misaeng = False
    if use_misaeng:
        misaeng_json = open(json_dir + 'misaeng.json', 'r', encoding='utf-8')
        default_data = json.load(misaeng_json)
        metadata_class = class_from_dict(default_data)
    else:
        default_data = {'opus_id': "1005", "opus_name__kr": "예시",  "opus_name__en": "Example"}
        metadata_class = Opus.from_dict(default_data)

    # set default values and update ids
    metadata_class.init_class_variables()
    metadata_class.update_metadata()

    # get opus dict(), scene dict() and shot dict()
    scene_idx = 0
    shot_idx = 0

    opus_dict = metadata_class.to_dict()

    scene_class = metadata_class.seasons[0].episodes[0].sequences[0].scenes[scene_idx]
    scene_dict = scene_class.to_dict()

    shot_class = scene_class.shots[shot_idx]
    shot_dict = shot_class.to_dict()

    # print opus, scene, shot to JSON file
    opus_file = open(json_dir + '{}.json'.format(default_data['opus_id']), 'w', encoding='utf-8')
    scene_file = open(json_dir + '{}_scene_{}.json'.format(default_data['opus_id'], scene_idx), 'w', encoding='utf-8')
    shot_file = open(json_dir + '{}_scene_{}_shot_{}.json.'.format(default_data['opus_id'], scene_idx, shot_idx), 'w', encoding='utf-8')
    json.dump(opus_dict, opus_file, indent=2, ensure_ascii=False)
    json.dump(scene_dict, scene_file, indent=2, ensure_ascii=False)
    json.dump(shot_dict, shot_file, indent=2, ensure_ascii=False)
    print("{}.json is finished".format(opus_dict))
