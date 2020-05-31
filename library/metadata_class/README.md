<hr>

#1. 한국어
## 클래스 함수 설명
1) from_dict
    - dict 변수를 Class로 변환하는 함수
    - 만약 dict 변수에 Class key값이 없을 경우, default 값으로 설정
    - 예시

            opus_dict = {opus_id: '1234'}
            opus_class = from_dict(opus_dict)
            print(opus_class.__dict__.items())
            
            >> ['opus_id': '1234', 'opus_name__kr': '', 'opus_name__en': '', 'seasons': []]

2) to_dict
    - 클래스 변수를 dict으로 변환하는 함수

## 메타데이터 구조 업데이트하는 방법
1. 파이썬 코드 수정
    - 수정하고자 하는 메타데이터 클래스에 속성(변수)을 추가
    - ex) <code>opus.py</code>를 <code>opus_change_version.py</code>와 같이 수정
2. \_\_init__.py 실행
    - 실제 데이터상에서 구조를 체크하고자 할 경우, <code>use_misaeng=True</code>로 설정
    - 단순히 구조만 체크하고자 할 경우, <code>use_misaeng=False</code>로 설정
3. JSON 파일 확인
    - <code>1001.json, 1001_scene_0.json, 1001_scene_0_shot_0.json</code>
        - <code>misaeng.json</code>를 기반으로 전체, Scene 번호 0, Scene 번호 0 및 Shot 번호 0 인 경우의 구조를 보여줌
    - <code>1005.json, 1005_scene_0.json, 1005_scene_0_shot_0.json</code>
        - 비어있는 전체, Scene 번호 0, Scene 번호 0 및 Shot 번호 0 인 경우의 구조를 보여줌

<hr/>

#2. English
## Class Method Description
1) from_dict()
    - function that convert dict() to Class
    - if dict() has no key of Class, Class object set default value
    - example
    
            opus_dict = {opus_id: '1234'}
            opus_class = from_dict(dict)
            print(opus_class.__dict__.items())
            
            ['opus_id': '1234', 'opus_name__kr': '', 'opus_name__en': '', 'seasons': []]

2) to_dict()
    - function that convert Class to dict

## How to update architecture
1. revise python class code
    - Add attributes(variables) to metadata class you want to modify
    - ex) convert <code>opus.py</code> to <code>opus_change_version.py</code>
2. run \_\_init__.py
    - if you want to architecture with real data, set <code>use_misaeng=True</code>
    - if you want to check architecture only, set <code>use_misaeng=False</code>
3. check .json file
    - <code>1001.json, 1001_scene_0.json, 1001_scene_0_shot_0.json</code>
        - show total, scene #=0, scene #=0 and shot #=0 architecture using <code>misaeng.json</code>
    - <code>1005.json, 1005_scene_0.json, 1005_scene_0_shot_0.json</code>
        - show total, scene #=0, scene #=0 and shot #=0 empty architecture

<hr/>

#3. Total Architecture
    Example of Opus, Season, Episode
    ex) bigbang theorie, season 12, episode 20
        - opus_id : 1050
        - season_id: 10500012
        - episode_id : 105000120020
        
    <Opus> : metadata of video
        opus_id: str
        opus_name__kr: str
        opus_name__en: str
        seasons: List[Season]
        <Season> : metadata of season
            season_id: str
            opus_id: str
            season_title__kr: str
            season_title__en: str
            episodes: List[Episode]
            <Episode> : metadata of episode
                episode_id: str
                season_id: str
                fps: float
                sequences: List[Sequence]
                <Sequence> : metadata of sub story plot of episode
                    sequence_id: str
                    episode_id: str
                    sequence_title: str
                    scenes: List[Scene]
                    <Scene> : metadata of scene
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
                        space: Space
                        <Space> : metadata of location and time
                            location_time: Optional[str]
                            location_type: Optional[str]
                            location: str
                            time: str
                        plot: List[Plot]
                        <Plot> : metadata of script(대본)
                            type: TypeEnum
                            explanation: Optional[str]
                            character: Optional[str]
                            dialogue: Optional[str]
                        script_scene_conflict: Optional[float]
                        scene_conflict_avg: Optional[List[float]]
                        sequence_title: str
                        conflict: Conflict
                        <Conflict> : metadata of conflict factor
                            factor: Optional[str]
                            step: Optional[str]
                            atmosphere: List[str]
                            related_scene: List[str]
                        shots: List[Shot]
                        <Shot> : metadata of shot
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
                            <KeyframesNum> : metadata of keyframe images in shot
                                keyframe_num_scene: int
                                keyframe_num_episode: int
                                keyframe_image_filename: str
                                keyframe_action: Optional[str]
                                keyframe_action_conflict: Optional[int]
                            faces: Optional[List[Face]] : No use
                            sounds: Optional[List[Sound]] : No use
                            shot_conflict_avg: Optional[List[float]]
                            persons: List[Person]
                            <Person> : metadata of a person
                                faces: List[Face]
                                <Face> : metadata of face object per person
                                    face_frame_num: Optional[int]
                                    face_time: Optional[str]
                                    face_xywh: List[float]
                                    face_name: Optional[str]
                                    face_emotion: List[float]
                                    face_actor_name: Optional[str]
                                    face_expression: Optional[str]
                                    face_intensity: Optional[float]
                                speeches: List[Speech]
                                <Speech> : metadata of natural language
                                    word_class_name: List[str]
                                    word_class_value: List[str]
                                    intensity: Optional[float]
                                positions: List[Position]
                                <Position> : metadata of location of person object
                                    position_frame_num: Optional[int]
                                    position_time: Optional[str]
                                    position_xywh: List[float]
                            actions: List[Action]
                            <Action> : metadata of action in shot
                                action_name: Optional[str]
                                action_score: Optional[float]
