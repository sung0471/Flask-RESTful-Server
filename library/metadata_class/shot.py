from library.metadata_class.convert_type import *
from library.metadata_class.root_class import MetadataClass
from utils.video_control import get_frame_to_time


class KeyframesNum:
    keyframe_num_scene: int
    keyframe_num_episode: int
    keyframe_image_filename: str
    keyframe_action: Optional[str]
    keyframe_action_conflict: Optional[int]

    def __init__(self, keyframe_num_scene: int, keyframe_num_episode: int, keyframe_image_filename: str,
                 keyframe_action: Optional[str], keyframe_action_conflict: Optional[int]) -> None:
        self.keyframe_num_scene = keyframe_num_scene
        self.keyframe_num_episode = keyframe_num_episode
        self.keyframe_image_filename = keyframe_image_filename
        self.keyframe_action = keyframe_action
        self.keyframe_action_conflict = keyframe_action_conflict

    @staticmethod
    def from_dict(obj: Any) -> 'KeyframesNum':
        assert isinstance(obj, dict)
        keyframe_num_scene = from_int(obj.get("keyframe_num_scene")) if "keyframe_num_scene" in obj.keys() else -1
        keyframe_num_episode = from_int(int(obj.get("keyframe_num_episode"))) if "keyframe_num_episode" in obj.keys() else -1
        keyframe_image_filename = from_str(obj.get("keyframe_image_filename")) if "keyframe_image_filename" in obj.keys() else ''
        keyframe_action = from_union([from_none, from_str], obj.get("keyframe_action"))
        keyframe_action_conflict = from_union([from_none, from_int], obj.get("keyframe_action_conflict"))
        return KeyframesNum(keyframe_num_scene, keyframe_num_episode, keyframe_image_filename, keyframe_action,
                            keyframe_action_conflict)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["keyframe_num_scene"] = from_int(self.keyframe_num_scene)
        result["keyframe_num_episode"] = from_int(self.keyframe_num_episode)
        result["keyframe_image_filename"] = from_str(self.keyframe_image_filename)
        result["keyframe_action"] = from_union([from_none, from_str], self.keyframe_action)
        result["keyframe_action_conflict"] = from_union([from_none, from_int], self.keyframe_action_conflict)
        return result


class Face:
    face_frame_num: Optional[int]
    face_time: Optional[str]
    face_xywh: List[float]
    face_name: Optional[str]
    face_emotion: List[float]
    face_actor_name: Optional[str]
    face_expression: Optional[str]
    face_intensity: Optional[float]

    def __init__(self, face_frame_num: Optional[int], face_time: Optional[str], face_xywh: List[float],
                 face_name: Optional[str], face_emotion: List[float], face_actor_name: Optional[str],
                 face_expression: Optional[str], face_intensity: Optional[float]) -> None:
        self.face_frame_num = face_frame_num
        self.face_time = face_time
        self.face_xywh = face_xywh
        self.face_name = face_name
        self.face_emotion = face_emotion
        self.face_actor_name = face_actor_name
        self.face_expression = face_expression
        self.face_intensity = face_intensity

    @staticmethod
    def from_dict(obj: any) -> 'Face':
        assert isinstance(obj, dict)
        face_frame_num = from_union([from_none, from_int], obj.get("face_frame_num"))
        face_time = from_union([from_none, from_str], obj.get("face_time"))
        face_xywh = from_list(from_float, obj.get("face_xywh")) if "face_xywh" in obj.keys() else list()
        face_name = from_union([from_none, from_str], obj.get("face_name"))
        face_emotion = from_list(from_float, obj.get("face_emotion")) if "face_emotion" in obj.keys() else list()
        face_actor_name = from_union([from_none, from_str], obj.get("face_actor_name"))
        face_expression = from_union([from_none, from_str], obj.get("face_expression"))
        face_intensity = from_union([from_none, from_float], obj.get("face_intensity"))
        return Face(face_frame_num, face_time, face_xywh, face_name, face_emotion,
                    face_actor_name, face_expression, face_intensity)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["face_frame_num"] = from_union([from_none, from_int], self.face_frame_num)
        result["face_time"] = from_union([from_none, from_str], self.face_time)
        result["face_xywh"] = from_list(from_float, self.face_xywh)
        result["face_name"] = from_union([from_none, from_str], self.face_name)
        result["face_emotion"] = from_list(from_float, self.face_emotion)
        result["face_actor_name"] = from_union([from_none, from_str], self.face_actor_name)
        result["face_expression"] = from_union([from_none, from_str], self.face_expression)
        result["face_intensity"] = from_union([from_none, from_float], self.face_intensity)
        return result

    def update_time(self, fps):
        if self.face_frame_num is not None:
            _, self.face_time = get_frame_to_time(self.face_frame_num, fps)


class Sound:
    sound_frame_num: Optional[str]
    sound_time: Optional[str]
    sound_conflict: Optional[float]

    def __init__(self, sound_frame_num: Optional[str], sound_time: Optional[str],
                 sound_conflict: Optional[float]) -> None:
        self.sound_frame_num = sound_frame_num
        self.sound_time = sound_time
        self.sound_conflict = sound_conflict

    @staticmethod
    def from_dict(obj: any) -> 'Sound':
        assert isinstance(obj, dict)
        sound_frame_num = from_union([from_none, from_str], obj.get("sound_frame_num"))
        sound_time = from_union([from_none, from_str], obj.get("sound_time"))
        sound_conflict = from_union([from_none, from_float], obj.get("sound_conflict"))
        return Sound(sound_frame_num, sound_time, sound_conflict)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["sound_frame_num"] = from_union([from_none, from_str], self.sound_frame_num)
        result["sound_time"] = from_union([from_none, from_str], self.sound_time)
        result["sound_conflict"] = from_union([from_none, from_float], self.sound_conflict)
        return result


class Speech:
    word_class_name: List[str]
    word_class_value: List[str]
    intensity: Optional[float]

    def __init__(self, word_class_name: List[str], word_class_value: List[str], intensity: Optional[float]) -> None:
        self.word_class_name = word_class_name
        self.word_class_value = word_class_value
        self.intensity = intensity

    @staticmethod
    def from_dict(obj: any) -> 'Speech':
        assert isinstance(obj, dict)
        word_class_name = from_list(from_str, obj.get("word_class_name")) if "word_class_name" in obj.keys() else list()
        word_class_value = from_list(from_str, obj.get("word_class_value")) if "word_class_value" in obj.keys() else list()
        intensity = from_union([from_none, from_float], obj.get("intensity"))
        return Speech(word_class_name, word_class_value, intensity)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["word_class_name"] = from_list(from_str, self.word_class_name)
        result["word_class_value"] = from_list(from_str, self.word_class_value)
        result["intensity"] = from_union([from_none, from_float], self.intensity)
        return result


class Position:
    position_frame_num: Optional[int]
    position_time: Optional[str]
    position_xywh: List[float]

    def __init__(self, position_frame_num: Optional[int], position_time: Optional[str],
                 position_xywh: List[float]) -> None:
        self.position_frame_num = position_frame_num
        self.position_time = position_time
        self.position_xywh = position_xywh

    @staticmethod
    def from_dict(obj: any) -> 'Position':
        assert isinstance(obj, dict)
        position_frame_num = from_union([from_none, from_int], obj.get("position_frame_num"))
        position_time = from_union([from_none, from_str], obj.get("position_time"))
        position_xywh = from_list(from_float, obj.get("position_xywh")) if "position_xywh" in obj.keys() else list()
        return Position(position_frame_num, position_time, position_xywh)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["position_frame_num"] = from_union([from_none, from_int], self.position_frame_num)
        result["position_time"] = from_union([from_none, from_str], self.position_time)
        result["position_xywh"] = from_list(from_float, self.position_xywh)
        return result

    def update_time(self, fps):
        if self.position_frame_num is not None:
            _, self.position_time = get_frame_to_time(self.position_frame_num, fps)


class Person(MetadataClass):
    faces: List[Face]
    speeches: List[Speech]
    positions: List[Position]

    default_key_value = {
        "faces": Face.from_dict(dict()),
        "speeches": Speech.from_dict(dict()),
        "positions": Position.from_dict(dict())
    }

    def __init__(self, faces: List[Face], speeches: List[Speech], positions: List[Position]) -> None:
        self.faces = faces
        self.speeches = speeches
        self.positions = positions

    @staticmethod
    def from_dict(obj: Any) -> 'Person':
        assert isinstance(obj, dict)
        faces = from_list(Face.from_dict, obj.get("faces")) if "faces" in obj.keys() else list()
        speeches = from_list(Speech.from_dict, obj.get("speeches")) if "speeches" in obj.keys() else list()
        positions = from_list(Position.from_dict, obj.get("positions")) if "positions" in obj.keys() else list()
        return Person(faces, speeches, positions)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["faces"] = from_list(lambda x: to_class(Face, x), self.faces)
        result["speeches"] = from_list(lambda x: to_class(Speech, x), self.speeches)
        result["positions"] = from_list(lambda x: to_class(Position, x), self.positions)
        return result


class Action:
    action_name: Optional[str]
    action_score: Optional[float]

    def __init__(self, action_name: Optional[str], action_score: Optional[float]) -> None:
        self.action_name = action_name
        self.action_score = action_score

    @staticmethod
    def from_dict(obj: Any) -> 'Action':
        assert isinstance(obj, dict)
        action_name = from_union([from_none, from_str], obj.get("action_name"))
        action_score = from_union([from_none, from_str], obj.get("action_score"))
        return Action(action_name, action_score)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["action_name"] = from_union([from_none, from_str], self.action_name)
        result["action_score"] = from_union([from_none, from_str], self.action_score)
        return result


class Shot(MetadataClass):
    v_scene_id: str
    v_shot_id: str
    start_frame_num_scene: int
    end_frame_num_scene: int
    start_time_scene: str
    end_time_scene: str
    start_second_scene: float
    end_second_scene: float
    start_frame_num_episode: int
    end_frame_num_episode: int
    start_time_episode: str
    end_time_episode: str
    start_second_episode: float
    end_second_episode: float
    duration_time: str
    keyframes_num: List[KeyframesNum]
    faces: Optional[List[Face]]
    sounds: Optional[List[Sound]]
    shot_conflict_avg: Optional[List[float]]
    persons: List[Person]
    actions: List[Action]

    default_key_value = {
        "persons": Person.from_dict(dict()),
        "actions": Action.from_dict(dict())
    }

    def __init__(self, v_scene_id: str, v_shot_id: str, start_frame_num_scene: int, end_frame_num_scene: int,
                 start_time_scene: str, end_time_scene: str, start_second_scene: float, end_second_scene: float,
                 start_frame_num_episode: int, end_frame_num_episode: int, start_time_episode: str,
                 end_time_episode: str, start_second_episode: float, end_second_episode: float, duration_time: str,
                 keyframes_num: List[KeyframesNum], faces: Optional[List[Face]], sounds: Optional[List[Sound]],
                 shot_conflict_avg: Optional[List[float]], persons: List[Person], actions: List[Action]) -> None:
        self.v_scene_id = v_scene_id
        self.v_shot_id = v_shot_id
        self.start_frame_num_scene = start_frame_num_scene
        self.end_frame_num_scene = end_frame_num_scene
        self.start_time_scene = start_time_scene
        self.end_time_scene = end_time_scene
        self.start_second_scene = start_second_scene
        self.end_second_scene = end_second_scene
        self.start_frame_num_episode = start_frame_num_episode
        self.end_frame_num_episode = end_frame_num_episode
        self.start_time_episode = start_time_episode
        self.end_time_episode = end_time_episode
        self.start_second_episode = start_second_episode
        self.end_second_episode = end_second_episode
        self.duration_time = duration_time
        self.keyframes_num = keyframes_num
        self.faces = faces
        self.sounds = sounds
        self.shot_conflict_avg = shot_conflict_avg
        self.persons = persons
        self.actions = actions

    @staticmethod
    def from_dict(obj: Any) -> 'Shot':
        assert isinstance(obj, dict)
        v_scene_id = from_str(obj.get("v_scene_id")) if "v_scene_id" in obj.keys() else ''
        v_shot_id = from_str(obj.get("v_shot_id")) if "v_shot_id" in obj.keys() else ''
        start_frame_num_scene = from_int(obj.get("start_frame_num_scene")) if "start_frame_num_scene" in obj.keys() else -1
        end_frame_num_scene = from_int(obj.get("end_frame_num_scene")) if "end_frame_num_scene" in obj.keys() else -1
        start_time_scene = from_str(obj.get("start_time_scene")) if "start_time_scene" in obj.keys() else ''
        end_time_scene = from_str(obj.get("end_time_scene")) if "end_time_scene" in obj.keys() else ''
        start_second_scene = from_float(obj.get("start_second_scene")) if "start_second_scene" in obj.keys() else -1.0
        end_second_scene = from_float(obj.get("end_second_scene")) if "end_second_scene" in obj.keys() else -1.0
        start_frame_num_episode = from_int(obj.get("start_frame_num_episode")) if "start_frame_num_episode" in obj.keys() else -1
        end_frame_num_episode = from_int(obj.get("end_frame_num_episode")) if "end_frame_num_episode" in obj.keys() else -1
        start_time_episode = from_str(obj.get("start_time_episode")) if "start_time_episode" in obj.keys() else ''
        end_time_episode = from_str(obj.get("end_time_episode")) if "end_time_episode" in obj.keys() else ''
        start_second_episode = from_float(obj.get("start_second_episode")) if "start_second_episode" in obj.keys() else -1.0
        end_second_episode = from_float(obj.get("end_second_episode")) if "end_second_episode" in obj.keys() else -1.0
        duration_time = from_str(obj.get("duration_time")) if "duration_time" in obj.keys() else ''
        keyframes_num = from_list(KeyframesNum.from_dict, obj.get("keyframes_num")) if "keyframes_num" in obj.keys() else list()
        faces = from_union([from_none, lambda x: from_list(Face.from_dict, x)], obj.get("faces"))
        sounds = from_union([from_none, lambda x: from_list(Sound.from_dict, x)], obj.get("sounds"))
        shot_conflict_avg = from_union([from_none, lambda x: from_list(from_float, x)], obj.get("shot_conflict_avg"))
        persons = from_list(Person.from_dict, obj.get("persons")) if "persons" in obj.keys() else list()
        actions = from_list(Action.from_dict, obj.get("actions")) if "actions" in obj.keys() else list()
        return Shot(v_scene_id, v_shot_id, start_frame_num_scene, end_frame_num_scene, start_time_scene, end_time_scene,
                    start_second_scene, end_second_scene, start_frame_num_episode, end_frame_num_episode,
                    start_time_episode, end_time_episode, start_second_episode, end_second_episode, duration_time,
                    keyframes_num, faces, sounds, shot_conflict_avg, persons, actions)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["v_scene_id"] = from_str(self.v_scene_id)
        result["v_shot_id"] = from_str(self.v_shot_id)
        result["start_frame_num_scene"] = from_int(self.start_frame_num_scene)
        result["end_frame_num_scene"] = from_int(self.end_frame_num_scene)
        result["start_time_scene"] = from_str(self.start_time_scene)
        result["end_time_scene"] = from_str(self.end_time_scene)
        result["start_second_scene"] = to_float(self.start_second_scene)
        result["end_second_scene"] = to_float(self.end_second_scene)
        result["start_frame_num_episode"] = from_int(self.start_frame_num_episode)
        result["end_frame_num_episode"] = from_int(self.end_frame_num_episode)
        result["start_time_episode"] = from_str(self.start_time_episode)
        result["end_time_episode"] = from_str(self.end_time_episode)
        result["start_second_episode"] = to_float(self.start_second_episode)
        result["end_second_episode"] = to_float(self.end_second_episode)
        result["duration_time"] = from_str(self.duration_time)
        result["keyframes_num"] = from_list(lambda x: to_class(KeyframesNum, x), self.keyframes_num)
        result["faces"] = from_union([from_none, lambda x: from_list(lambda x: to_class(Face, x), x)], self.faces)
        result["sounds"] = from_union([from_none, lambda x: from_list(lambda x: to_class(Sound, x), x)], self.sounds)
        result["shot_conflict_avg"] = from_union([from_none, lambda x: from_list(from_float, x)],
                                                 self.shot_conflict_avg)
        result["persons"] = from_list(lambda x: to_class(Person, x), self.persons)
        result["actions"] = from_list(lambda x: to_class(Action, x), self.actions)
        return result

    def update_shot_data(self, scene_id=None, idx=None, fps=None, start_frame_num_of_scene=None):
        """
            scene_id를 받아서 모든 메타데이터 id를 수정하고,
            episode의 fps를 넘겨서 모든 second, time 변수들을 수정하도록 수행
            set all metadata ids using scene_id
            and
            set all second, time variables in metadata class using fps and frame_num
        """
        if isinstance(scene_id, str) and isinstance(idx, int) and isinstance(start_frame_num_of_scene, int):
            self.v_scene_id = scene_id
            idx_str = str(idx + 1)
            self.v_shot_id = scene_id + '0' * (4 - len(idx_str)) + idx_str
        elif scene_id is None and idx is None:
            pass
        else:
            assert False, 'scene_id, idx = [None, None] or [str, int]'

        if fps is not None:
            self.start_frame_num_scene = self.start_frame_num_episode - start_frame_num_of_scene
            self.end_frame_num_scene = self.end_frame_num_episode - start_frame_num_of_scene
            duration = self.end_frame_num_scene - self.start_frame_num_scene

            self.start_second_episode, self.start_time_episode = get_frame_to_time(self.start_frame_num_episode, fps)
            self.end_second_episode, self.end_time_episode = get_frame_to_time(self.end_frame_num_episode, fps)

            self.start_second_scene, self.start_time_scene = get_frame_to_time(self.start_frame_num_scene, fps)
            self.end_second_scene, self.end_time_scene = get_frame_to_time(self.end_frame_num_scene, fps)
            _, self.duration_time = get_frame_to_time(duration, fps)

            for key_frames_num_class in self.keyframes_num:
                key_frames_num_class.keyframe_num_scene = key_frames_num_class.keyframe_num_episode - start_frame_num_of_scene

            for person_ins in self.persons:
                class_list = [person_ins.faces, person_ins.positions]
                for class_ins_list in class_list:
                    for class_ins in class_ins_list:
                        class_ins.update_time(fps=fps)
