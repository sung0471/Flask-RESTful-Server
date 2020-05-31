from library.metadata_class.convert_type import *
from library.metadata_class.root_class import MetadataClass
from library.metadata_class.season import Season


class Opus(MetadataClass):
    opus_id: str
    opus_name__kr: str
    opus_name__en: str
    seasons: List[Season]

    default_key_value = {
        "seasons": Season.from_dict(dict())
    }

    def __init__(self, opus_id: str, opus_name__kr: str, opus_name__en: str, seasons: List[Season]) -> None:
        self.opus_id = opus_id if isinstance(opus_id, str) else str(opus_id)
        self.opus_name__kr = opus_name__kr
        self.opus_name__en = opus_name__en
        self.seasons = seasons

    @staticmethod
    def from_dict(obj: Any) -> 'Opus':
        assert isinstance(obj, dict)
        opus_id = from_str(obj.get("opus_id")) if "opus_id" in obj.keys() else ''
        opus_name__kr = from_str(obj.get("opus_name__kr")) if "opus_name__kr" in obj.keys() else ''
        opus_name__en = from_str(obj.get("opus_name__en")) if "opus_name__en" in obj.keys() else ''
        seasons = from_list(Season.from_dict, obj.get("seasons"))if "seasons" in obj.keys() else list()
        return Opus(opus_id, opus_name__kr, opus_name__en, seasons)

    def to_dict(self) -> dict:
        result: dict = dict()
        result["opus_id"] = from_str(self.opus_id)
        result["opus_name__kr"] = from_str(self.opus_name__kr)
        result["opus_name__en"] = from_str(self.opus_name__en)
        result["seasons"] = from_list(lambda x: to_class(Season, x), self.seasons)
        return result

    def update_metadata(self):
        """
            opus_id로 모든 메타데이의 id를 수정함
            set all metadata ids using opus_id
        """
        for i in range(len(self.seasons)):
            self.seasons[i].update_season_id(opus_id=self.opus_id, idx=i)
