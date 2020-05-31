from library.metadata_class.convert_type import *
from library.metadata_class.root_class import MetadataClass
from library.metadata_class.scene import Scene


class Sequence(MetadataClass):
    sequence_id: str
    episode_id: str
    sequence_title: str
    scenes: List[Scene]

    default_key_value = {
        "scenes": Scene.from_dict(dict())
    }

    def __init__(self, sequence_id: str, episode_id: str, sequence_title: str, scenes: List[Scene]) -> None:
        self.sequence_id = sequence_id
        self.episode_id = episode_id
        self.sequence_title = sequence_title
        self.scenes = scenes

    @staticmethod
    def from_dict(obj: Any) -> 'Sequence':
        assert isinstance(obj, dict)
        sequence_id = from_str(obj.get("sequence_id")) if "sequence_id" in obj.keys() else ''
        episode_id = from_str(obj.get("episode_id")) if "episode_id" in obj.keys() else ''
        sequence_title = from_str(obj.get("sequence_title")) if "sequence_title" in obj.keys() else ''
        scenes = from_list(Scene.from_dict, obj.get("scenes")) if "scenes" in obj.keys() else list()
        return Sequence(sequence_id, episode_id, sequence_title, scenes)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["sequence_id"] = from_str(self.sequence_id)
        result["episode_id"] = from_str(self.episode_id)
        result["sequence_title"] = from_str(self.sequence_title)
        result["scenes"] = from_list(lambda x: to_class(Scene, x), self.scenes)
        return result

    def update_sequence_data(self, episode_id=None, idx=None, fps=None):
        """
            episode_id를 받아서 모든 메타데이터 id를 수정하고,
            episode의 fps를 넘겨서 모든 second, time 변수들을 수정하도록 수행
            set all metadata ids using episode_id
            and
            set all second, time variables in metadata class using fps and frame_num
        """
        if isinstance(episode_id, str) and isinstance(idx, int):
            self.episode_id = episode_id
            idx_str = str(idx + 1)
            self.sequence_id = episode_id + '0' * (4 - len(idx_str)) + idx_str
        elif episode_id is None and idx is None:
            pass
        else:
            assert False, 'episode_id, idx = [None, None] or [str, int]'

        for i in range(len(self.scenes)):
            self.scenes[i].update_scene_data(sequence_id=self.sequence_id, idx=i, fps=fps)
