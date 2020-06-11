import json
import os

from library.make_people_list import get_people_list
# from library.serialization import TypeEnum, welcome_from_dict, UseFlag
from library.metadata_class import TypeEnum, class_from_dict, UseFlag
from library.directory_control import get_file_dir_path

null = None


def is_not_null(obj):
    if obj == null:
        return 0
    else:
        return len(obj)


def match_number_length(number, length):
    str_number = str(number)
    str_length = len(str_number)
    if str_length < length:
        return_value = "0"*(length-str_length) + str_number
    else:
        return_value = str_number
    return return_value


def data_split(deserial):
    # episode 단위로 자르기
    # 각 배열엔 각 Episode 객체가 있음
    episodes = deserial.seasons[0].episodes

    # episode별 Sequnce 단위로 자르기
    # 각 배열엔 각 episode별 Sequence 객체가 있음
    sequences = [[] for _ in range(len(episodes))]
    for i, episode in enumerate(episodes):
        for j, sequence in enumerate(episode.sequences):
            sequences[i].append(sequence)

    # episode별 Scene 단위로 자르기
    # 각 배열엔 각 episode별 Scene 객체가 있음
    scenes = [[] for _ in range(len(episodes))]
    scene_count_info = {"sceneCount": [0] * len(episodes),
                        "sceneArrayCount": [0] * len(episodes)}  # scene 개수가 있는 배열

    for i, sequence_list in enumerate(sequences):
        for j, sequence in enumerate(sequence_list):
            for k, scene in enumerate(sequence.scenes):
                if scene.use_flag == UseFlag.Y:
                    scenes[i].append(scene)
        scene_count_info["sceneCount"][i] = len(scenes[i])
        scene_count_info["sceneArrayCount"][i] = len(scenes[i])+1

    return scenes, scene_count_info


def data_rendering(scenes, sceneCountInfo):
    # 각 에피소드별 sceneArray 개수 정보를 dataArr에 추가
    data_arr = {"episodeLength": sceneCountInfo["sceneArrayCount"],
                "sceneNumber": list()}

    # sceneNumber 이름들을 dataArr에 추가
    for i,number in enumerate(sceneCountInfo["sceneCount"]):
        for j in range(number):
            scene_number = "S"+str(j+1)
            data_arr["sceneNumber"].append(scene_number)
        name_of_total_people_in_episode="E"+str(i+1)+" total"
        data_arr["sceneNumber"].append(name_of_total_people_in_episode)

    # scene 개수 / sceneArray의 총 합
    sceneCountInfo["sceneCount"].append(sum(sceneCountInfo["sceneCount"]))
    sceneCountInfo["sceneArrayCount"].append(sum(sceneCountInfo["sceneArrayCount"]))

    # peopleList를 받아 해당 peopleList를 기준으로 사전(dict)생성
    people_list = get_people_list()               # 정리된 peoplelist 데이터를 받음
    data_statistic = dict()
    for name in people_list[0]:
        default_arr = [0] * (sceneCountInfo["sceneArrayCount"][len(sceneCountInfo["sceneArrayCount"]) - 1])  # sceneArray 개수의 합만큼 배열생성
        data_arr[name] = default_arr
        data_statistic[name] = {"isSeen": 0, "totalSceneNumber": 0,
                                "startScene": "", "endScene": ""}

    # 인물 별 등장 횟수 -> array로 정리
    for i in range(len(scenes)):                        # episode 수 만큼 iteration
        for j, scene_obj in enumerate(scenes[i]):             # scenes 배열의 scene 객체들을 전부 iteration
            if is_not_null(scene_obj.plot):                        # scene 객체의 plot변수가 비어있지 않은 경우
                for plot_obj in scene_obj.plot:                       # plot변수의 plot객체들 전부 iteration
                    if plot_obj.type is not None and plot_obj.type.value == TypeEnum.DIALOGUE.value:     # plot 객체의 type변수의 값 = "dialogue"인 경우
                        if plot_obj.character in people_list[1]:              # plot 객체의 character 변수가 존재하는 이름인 경우
                            data_arr[people_list[1][plot_obj.character]][sum(sceneCountInfo["sceneArrayCount"][0:i])+j] += 1    # 등장유무 체크
                            data_arr[people_list[1][plot_obj.character]][sum(sceneCountInfo["sceneArrayCount"][0:i+1])-1] += 1    # 등장유무 총합 체크
                            data_statistic[people_list[1][plot_obj.character]]["totalSceneNumber"] += 1
                            epi_scene_number = "E" + match_number_length(i + 1, 2) + " " + "S" + match_number_length(j + 1, 3)
                            if data_statistic[people_list[1][plot_obj.character]]["isSeen"] == 0:   # 처음 등장한 경우
                                data_statistic[people_list[1][plot_obj.character]]["isSeen"] = 1    # 등장여부 체크
                                data_statistic[people_list[1][plot_obj.character]]["startScene"] = epi_scene_number  # 등장한 Episode+Scene의 위치를 저장
                            else:   # 두번째 등장한 경우 부터는
                                data_statistic[people_list[1][plot_obj.character]]["endScene"] = epi_scene_number    # 등장한 Episode+Scene의 위치를 저장

                # for name in arePeopleInScene:
                #     if arePeopleInScene[name]==1:
                #         dataArr[name][sum(sceneCount[0:i])+j]+=1   # 등장횟수 +1
                #         arePeopleInScene[name] = 0
    data_total = {"dataArr": data_arr,
                  "dataStatistic": data_statistic}
    return data_total


def data_print_to_file(metadataDir, dataArr, extension):
    with open(metadataDir + ".lifeCycle" + extension, 'w', encoding="utf-8") as file:
        json.dump(dataArr, file, indent=4, ensure_ascii=False)  # dict -> json


def get_data_total(file_path):
    file_name, extension = os.path.splitext(file_path)
    metadata_dir = get_file_dir_path(file_name)
    # metadata 디렉토리에 있는 파일 읽기
    # json > class 객체화
    with open(metadata_dir + extension, 'rt', encoding="utf-8") as file:
        json_file = json.load(file)                 # json -> dict
        data = class_from_dict(json_file)  # dict -> class(object)

    scenes, scene_count = data_split(data)      # class로된 데이터 쪼개서 Episode별 Scene 객체들로 저장
    lifecycle_data = data_rendering(scenes, scene_count)    # Scene안의 plot에서 인물등장횟수를 Scene별로 체크하여 저장
    data_print_to_file(metadata_dir, lifecycle_data, extension)      # 인물 라이프 사이클 데이터를 파일 출력

    return lifecycle_data
