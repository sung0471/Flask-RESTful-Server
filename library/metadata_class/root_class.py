class MetadataClass:
    """
    - 목적
        → 기본적으로 각 클래스에서 default를 설정하지만, Class list 변수들(seasons, episodes, ...)은 list()로만 정의
        → 이렇게 초기화하면 전체 architecture를 볼 수 없음. 그렇다고 각 클래스에 전체 구조를 알 수 있도록 추가하면, 메타데이터 양이 커짐
        → 구조만을 알기 위한 함수를 추가하기 위해 해당 부모 클래스를 구현
    """
    default_key_value = None

    def init_class_variables(self):
        """
            set class parameter to default values
            if default_key_value is None, this function don't operate
            ex) self.__dict__[key] = [Class.from_dict(dict())]

                Class Opus : self.seasons = [Season.from_dict(dict())]
                Class Season : self.episodes = [Episode.from_dict(dict())]
                Class Episode : self.sequences = [Sequence.from_dict(dict())]
                Class Sequence : self.scenes = [Scene.from_dict(dict())]
                Class Scene : self.shots = [Shot.from_dict(dict())]

            ex) self.default_key_value = {
                "seasons": Season.from_dict(dict())
            }
        """
        class_members_dict = self.__dict__
        if self.default_key_value is not None:
            for key, value in self.default_key_value.items():
                if len(class_members_dict[key]) == 0:
                    class_members_dict[key].append(value)
                for i in range(len(class_members_dict[key])):
                    parent_class_of_list = class_members_dict[key][i].__class__.__bases__[-1]
                    if parent_class_of_list == MetadataClass:
                        # child_class_members_dict = class_members_dict[key][i].__dict__
                        # if "default_key_value" in child_class_members_dict.keys():
                        class_members_dict[key][i].init_class_variables()
