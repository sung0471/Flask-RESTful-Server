from library.metadata_class.convert_type import *
from library.metadata_class.root_class import MetadataClass
from library.metadata_class.shot import Shot
from utils.video_control import get_frame_to_time


class Space:
    location_time: Optional[str]
    location_type: Optional[str]
    location: str
    time: str

    def __init__(self, location_time: Optional[str], location_type: Optional[str], location: str, time: str) -> None:
        self.location_time = location_time
        self.location_type = location_type
        self.location = location
        self.time = time

    @staticmethod
    def from_dict(obj: Any) -> 'Space':
        assert isinstance(obj, dict)
        location_time = from_union([from_none, from_str], obj.get("location_time"))
        location_type = from_union([from_none, from_str], obj.get("location_type"))
        location = from_str(obj.get("location")) if "location" in obj.keys() else ''
        time = from_str(obj.get("time")) if "time" in obj.keys() else ''
        return Space(location_time, location_type, location, time)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["location_time"] = from_union([from_none, from_str], self.location_time)
        result["location_type"] = from_union([from_none, from_str], self.location_type)
        result["location"] = from_str(self.location)
        result["time"] = from_str(self.time)
        return result


class TypeEnum(Enum):
    DIALOGUE = "dialogue"
    EXPLANATION = "explanation"


class Plot:
    type: TypeEnum
    explanation: Optional[str]
    character: Optional[str]
    dialogue: Optional[str]

    def __init__(self, type: TypeEnum, explanation: Optional[str], character: Optional[str],
                 dialogue: Optional[str]) -> None:
        self.type = type
        self.explanation = explanation
        self.character = character
        self.dialogue = dialogue

    @staticmethod
    def from_dict(obj: Any) -> 'Plot':
        assert isinstance(obj, dict)
        type = TypeEnum(obj.get("type"))
        explanation = from_union([from_str, from_none], obj.get("explanation"))
        character = from_union([from_str, from_none], obj.get("character"))
        dialogue = from_union([from_str, from_none], obj.get("dialogue"))
        return Plot(type, explanation, character, dialogue)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["type"] = to_enum(TypeEnum, self.type)
        # 수정부분 ---
        explanation = from_union([from_str, from_none], self.explanation)
        if explanation is None:
            pass
        else:
            result["explanation"] = explanation
        character = from_union([from_str, from_none], self.character)
        dialogue = from_union([from_str, from_none], self.dialogue)
        if character is None:
            pass
        else:
            result["character"] = character
            result["dialogue"] = dialogue
        # 수정부분 ---
        return result


class Conflict:
    factor: Optional[str]
    step: Optional[str]
    atmosphere: List[str]
    related_scene: List[str]

    def __init__(self, factor: Optional[str], step: Optional[str], atmosphere: List[Optional[str]], related_scene: List[Optional[str]]) -> None:
        self.factor = factor
        self.step = step
        self.atmosphere = atmosphere
        self.related_scene = related_scene

    @staticmethod
    def from_dict(obj: Any) -> 'Conflict':
        assert isinstance(obj, dict)
        factor = from_union([from_none, from_str], obj.get("factor"))
        step = from_union([from_none, from_str], obj.get("step"))
        atmosphere = from_list(from_str, obj.get("atmosphere")) if "atmosphere" in obj.keys() else list()
        related_scene = from_list(from_str, obj.get("related_scene")) if "related_scene" in obj.keys() else list()
        return Conflict(factor, step, atmosphere, related_scene)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["factor"] = from_union([from_none, from_str], self.factor)
        result["step"] = from_union([from_none, from_str], self.step)
        result["atmosphere"] = from_list(from_str, self.atmosphere)
        result["related_scene"] = from_list(from_str, self.related_scene)
        return result


class UseFlag(Enum):
    N = "N"
    Y = "Y"


class Scene(MetadataClass):
    scene_id: str
    sequence_id: str
    s_scene_id: Optional[str]
    v_scene_id: Optional[str]
    use_flag: UseFlag
    start_time: Optional[str]
    end_time: Optional[str]
    duration_time: Optional[str]
    v_location_time: Optional[str]
    start_frame_num: Optional[int]
    end_frame_num: Optional[int]
    start_second: Optional[float]
    end_second: Optional[float]
    shots: List[Shot]
    space: Space
    plot: List[Plot]
    script_scene_conflict: Optional[float]
    scene_conflict_avg: Optional[List[float]]
    sequence_title: str
    conflict: Conflict

    default_key_value = {
        "shots": Shot.from_dict(dict())
    }

    def __init__(self, scene_id: str, sequence_id: str, s_scene_id: Optional[str], v_scene_id: Optional[str], use_flag: UseFlag, start_time: Optional[str], end_time: Optional[str], duration_time: Optional[str], v_location_time: Optional[str], start_frame_num: Optional[int], end_frame_num: Optional[int], start_second: Optional[float], end_second: Optional[float], shots: List[Shot], space: Space, plot: List[Plot], script_scene_conflict: Optional[float], scene_conflict_avg: Optional[List[float]], sequence_title: str, conflict: Conflict) -> None:
        self.scene_id = scene_id
        self.sequence_id = sequence_id
        self.s_scene_id = s_scene_id
        self.v_scene_id = v_scene_id
        self.use_flag = use_flag
        self.start_time = start_time
        self.end_time = end_time
        self.duration_time = duration_time
        self.v_location_time = v_location_time
        self.start_frame_num = start_frame_num
        self.end_frame_num = end_frame_num
        self.start_second = start_second
        self.end_second = end_second
        self.shots = shots
        self.space = space
        self.plot = plot
        self.script_scene_conflict = script_scene_conflict
        self.scene_conflict_avg = scene_conflict_avg
        self.sequence_title = sequence_title
        self.conflict = conflict

    @staticmethod
    def from_dict(obj: Any) -> 'Scene':
        assert isinstance(obj, dict)
        scene_id = from_str(obj.get("scene_id")) if "scene_id" in obj.keys() else ''
        sequence_id = from_str(obj.get("sequence_id")) if "sequence_id" in obj.keys() else ''
        s_scene_id = from_union([from_none, from_str], obj.get("s_scene_id"))
        v_scene_id = from_union([from_none, from_str], obj.get("v_scene_id"))
        use_flag = UseFlag(obj.get("use_flag")) if "use_flag" in obj.keys() else UseFlag('Y')
        start_time = from_union([from_none, from_str], obj.get("start_time"))
        end_time = from_union([from_none, from_str], obj.get("end_time"))
        duration_time = from_union([from_none, from_str], obj.get("duration_time"))
        v_location_time = from_union([from_none, from_str], obj.get("v_location_time"))
        start_frame_num = from_union([from_int, from_none], obj.get("start_frame_num"))
        end_frame_num = from_union([from_int, from_none], obj.get("end_frame_num"))
        start_second = from_union([from_float, from_none], obj.get("start_second"))
        end_second = from_union([from_float, from_none], obj.get("end_second"))
        shots = from_list(Shot.from_dict, obj.get("shots")) if "shots" in obj.keys() else list()
        space = Space.from_dict(obj.get("space")) if "space" in obj.keys() and obj.get("space") is not None else Space.from_dict(dict())
        plot = from_list(Plot.from_dict, obj.get("plot")) if "plot" in obj.keys() and obj.get("plot") is not None else list()
        script_scene_conflict = from_union([from_float, from_none], obj.get("script_scene_conflict"))
        scene_conflict_avg = from_union([lambda x: from_list(from_float, x), from_none], obj.get("scene_conflict_avg"))
        sequence_title = from_str(obj.get("sequence_title")) if "sequence_title" in obj.keys() else ''
        conflict = Conflict.from_dict(obj.get("conflict")) if "conflict" in obj.keys() else Conflict.from_dict(dict())
        return Scene(scene_id, sequence_id, s_scene_id, v_scene_id, use_flag, start_time, end_time, duration_time, v_location_time, start_frame_num, end_frame_num, start_second, end_second, shots, space, plot, script_scene_conflict, scene_conflict_avg, sequence_title, conflict)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["scene_id"] = from_str(self.scene_id)
        result["sequence_id"] = from_str(self.sequence_id)
        result["s_scene_id"] = from_union([from_none, from_str], self.s_scene_id)
        result["v_scene_id"] = from_union([from_none, from_str], self.v_scene_id)
        result["use_flag"] = to_enum(UseFlag, self.use_flag)
        result["start_time"] = from_union([from_none, from_str], self.start_time)
        result["end_time"] = from_union([from_none, from_str], self.end_time)
        result["duration_time"] = from_union([from_none, from_str], self.duration_time)
        result["v_location_time"] = from_union([from_none, from_str], self.v_location_time)
        result["start_frame_num"] = from_union([from_int, from_none], self.start_frame_num)
        result["end_frame_num"] = from_union([from_int, from_none], self.end_frame_num)
        result["start_second"] = from_union([to_float, from_none], self.start_second)
        result["end_second"] = from_union([to_float, from_none], self.end_second)
        result["shots"] = from_list(lambda x: to_class(Shot, x), self.shots)
        result["space"] = to_class(Space, self.space)
        result["plot"] = from_list(lambda x: to_class(Plot, x), self.plot)
        result["script_scene_conflict"] = from_union([from_float, from_none], self.script_scene_conflict)
        result["scene_conflict_avg"] = from_union([lambda x: from_list(from_float, x), from_none], self.scene_conflict_avg)
        result["sequence_title"] = from_str(self.sequence_title)
        result["conflict"] = to_class(Conflict, self.conflict)
        return result

    def update_scene_data(self, sequence_id=None, idx=None, fps=None):
        """
            sequence_id를 받아서 모든 메타데이터 id를 수정하고,
            episode의 fps를 넘겨서 모든 second, time 변수들을 수정하도록 수행
            set all metadata ids using sequence_id
            and
            set all second, time variables in metadata class using fps and frame_num
        """
        if isinstance(sequence_id, str) and isinstance(idx, int):
            self.sequence_id = sequence_id
            idx_str = str(idx + 1)
            self.scene_id = sequence_id + '0' * (4 - len(idx_str)) + idx_str
        elif sequence_id is None and idx is None:
            pass
        else:
            assert False, 'sequence_id, idx = [None, None] or [str, int]'

        # frame, time revise
        if len(self.shots) != 0 and fps is not None:
            self.start_frame_num = self.shots[0].start_frame_num_episode
            self.end_frame_num = self.shots[-1].end_frame_num_episode
            duration = self.end_frame_num - self.start_frame_num

            self.start_second, self.start_time = get_frame_to_time(self.start_frame_num, fps)
            self.end_second, self.end_time = get_frame_to_time(self.end_frame_num, fps)
            _, self.duration_time = get_frame_to_time(duration, fps)

        for i in range(len(self.shots)):
            self.shots[i].update_shot_data(scene_id=self.scene_id, idx=i, fps=fps, start_frame_num_of_scene=self.start_frame_num)
