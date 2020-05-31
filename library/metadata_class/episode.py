from library.metadata_class.convert_type import *
from library.metadata_class.root_class import MetadataClass
from library.metadata_class.sequence import Sequence


class Episode(MetadataClass):
    episode_id: str
    season_id: str
    fps: float
    sequences: List[Sequence]

    default_key_value = {
        "sequences": Sequence.from_dict(dict())
    }

    def __init__(self, episode_id: str, season_id: str, fps: float, sequences: List[Sequence]) -> None:
        self.episode_id = episode_id
        self.season_id = season_id if isinstance(season_id, str) else str(season_id)
        self.fps = fps
        self.sequences = sequences

    @staticmethod
    def from_dict(obj: Any) -> 'Episode':
        assert isinstance(obj, dict)
        episode_id = from_str(obj.get("episode_id")) if "episode_id" in obj.keys() else ''
        season_id = from_str(obj.get("season_id")) if "season_id" in obj.keys() else ''
        fps = from_float(obj.get("fps")) if "fps" in obj.keys() else 29.97
        sequences = from_list(Sequence.from_dict, obj.get("sequences")) if "sequences" in obj.keys() else list()

        return Episode(episode_id, season_id, fps, sequences)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["episode_id"] = from_str(self.episode_id)
        result["season_id"] = from_str(self.season_id)
        result["fps"] = from_float(self.fps)
        result["sequences"] = from_list(lambda x: to_class(Sequence, x), self.sequences)
        return result

    def update_episode_data(self, season_id=None, idx=None):
        """
            season_id를 받아서 모든 메타데이터 id를 수정하고,
            episode의 fps를 넘겨서 모든 second, time 변수들을 수정하도록 수행
            set all metadata ids using season_id
            and
            set all second, time variables in metadata class using fps and frame_num
        """
        if isinstance(season_id, str) and isinstance(idx, int):
            self.season_id = season_id
            idx_str = str(idx + 1)
            self.episode_id = season_id + '0' * (4 - len(idx_str)) + idx_str
        elif season_id is None and idx is None:
            pass
        else:
            assert False, 'season_id, idx = [None, None] or [str, int]'

        for i in range(len(self.sequences)):
            self.sequences[i].update_sequence_data(episode_id=self.episode_id, idx=i, fps=self.fps)
