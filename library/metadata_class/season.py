from library.metadata_class.convert_type import *
from library.metadata_class.root_class import MetadataClass
from library.metadata_class.episode import Episode


class Season(MetadataClass):
    season_id: str
    opus_id: str
    season_title__kr: str
    season_title__en: str
    episodes: List[Episode]

    default_key_value = {
        "episodes": Episode.from_dict(dict())
    }

    def __init__(self, season_id: str, opus_id: str, season_title__kr: str, season_title__en: str, episodes: List[Episode]) -> None:
        self.season_id = season_id if isinstance(season_id, str) else str(season_id)
        self.opus_id = opus_id if isinstance(opus_id, str) else str(opus_id)
        self.season_title__kr = season_title__kr
        self.season_title__en = season_title__en
        self.episodes = episodes

    @staticmethod
    def from_dict(obj: Any) -> 'Season':
        assert isinstance(obj, dict)
        season_id = from_str(obj.get("season_id")) if "season_id" in obj.keys() else ''
        opus_id = from_str(obj.get("opus_id")) if "opus_id" in obj.keys() else ''
        season_title__kr = from_str(obj.get("season_title__kr")) if "season_title__kr" in obj.keys() else ''
        season_title__en = from_str(obj.get("season_title__en")) if "season_title__en" in obj.keys() else ''
        episodes = from_list(Episode.from_dict, obj.get("episodes")) if "episodes" in obj.keys() else list()
        return Season(season_id, opus_id, season_title__kr, season_title__en, episodes)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["season_id"] = from_str(str(self.season_id))
        result["opus_id"] = from_str(str(self.opus_id))
        result["season_title__kr"] = from_str(self.season_title__kr)
        result["season_title__en"] = from_str(self.season_title__en)
        result["episodes"] = from_list(lambda x: to_class(Episode, x), self.episodes)
        return result

    def update_season_id(self, opus_id=None, idx=None):
        """
            opus_id를 받아서 모든 메타데이터 id를 수정함
            set all metadata ids using opus_id
        """
        if isinstance(opus_id, str) and isinstance(idx, int):
            self.opus_id = opus_id
            idx_str = str(idx + 1)
            self.season_id = opus_id + '0' * (4 - len(idx_str)) + idx_str
        elif opus_id is None and idx is None:
            pass
        else:
            assert False, 'prefix, idx = None, None or str, int'

        for i in range(len(self.episodes)):
            self.episodes[i].update_episode_data(season_id=self.season_id, idx=i)
