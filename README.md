# Flask RESTful Server for Metadata DB

- 핵심 기능에 필요한 원본 메타데이터는 삭제되어있습니다.
- 따라서, 실제로 서버가 켜지는 기능만 가능합니다.

## Requirement
- Test (20.5.31)

        conda install --name flask_restful python=3.7
        activate flask_restful
        pip install flask-restful==0.3.6(origin ver)
                 or flask-restful ~0.3.8(recent ver)
        pip install moviepy==1.0.1(origin ver)
                or moviepy ~1.0.3(recent ver)
        pip install flask-cors==3.0.8(origin ver)
                or flask-cors ~3.0.8(recent ver)

## Directory Description
### /library/ : 함수들 정의해놓은 python 파일들이 있는 디렉토리
1. metadata_class : 메타데이터의 구조를 Class 객체로 선언한 파일
    - __init__.py : dict() ←→ Class 간의 변환함수 및 모든 python files import
    - convert_type.py : Type 선언 및 검증함수
    - opus.py, season.py, episode.py, sequence.py, scene.py, shot.py
      - 메타데이터 클래스를 선언한 파일
      - 각 클래스의 계층 단계(hierarchy Level)단위로 관리
    - README.md : 공통적으로 사용되는 함수, 사용법, 전체 구조를 설명한 파일
    
2. directory_control.py
    - 디렉토리나 경로를 제어하는 함수들을 포함하고 있는 파일

3. make_people_list.py (lifeCycle 용도)
    - 인물 정보를 읽어서 맵핑시켜주는 기능을 포함한 파일

4. people_in_scene.py (lifeCycle 용도)
    - lifeCycle을 계산하는 기능들이 포함된 파일

5. read_srt.py (lifeCycle 용도)
    - srt 파일을 읽고 처리하기 위한 파일

### /metadata/ : JSON 파일들이 있는 디렉토리
- [opus_name]/opus_origin.json
    - 최초 생성된 JSON파일을 백업한 버전
- [opus_name]/opus_name.json
    - 최초 생성 이후부터 지속적으로 사용하는 파일

### /utils/ : 클래스로 관리되는 python 파일들이 있는 디렉토리
- metadata_control.py : 메타데이터를 검색, 수정, 저장 등 관리하는 클래스
    - 관리하는 변수
        - self.class_data : 메타데이터를 클래스로 바꿔 저장한 변수
        - self.sequence_scene_shot_struct : 메타데이터의 구조 정보만 저장한 변수
        - self.cumulative_sum : 메타데이터의 Scene, Shot 개수의 누적합을 저장한 변수
    - "lifeCycle"생성에 사용되는 함수들을 해당 파일에 포함시킴
- time_control.py : 스톱워치 기능을 위한 클래스
- video_control.py : 영상 데이터를 관리하기 위한 클래스 및 함수가 포함된 파일

### / : 실행 파일들
- lifeCycle_api.py : life_cycle를 출력하기 위한 RESTful API
- metadata_input_api.py : 메타데이터 입력기에 필요한 기능을 제공하는 RESTful API
- requirements : window에서 metadata_input_api만을 위한 패키지 목록
- run.sh
    - metadata_input_api를 실행 가능한 명령어
    - log를 남기면서 Flask 서버를 돌리기 위한 shell 명령어

## API 설명
### - 공통 사항
- 모든 주소의 <code>Port=15000</code>로 설정되어있음
- 모든 API에서 Season, Episode, Sequence, Scene, Shot의 선택은 Get 파라미터로 진행함
    - 예를 들어, Season=1, Episode=2를 선택하고 싶을 경우
        - [IP:Port]/API_address?season=1&episode=2 로 접근
    - 모든 Default 값은 1
        - get으로 넘기지 않은 변수는 1로 사용됨
- Get 파라미터로 넘기는 값은 위 변수외에 2개가 더 있음
    - 총 7개 : season, episode, sequence, scene, shot, save, no_full
    - save : HTTP POST 방식으로 사용할 때만 사용됨
        - 수정하거나 임시저장한 뒤에, JSON파일에 저장하고 싶을 경우 사용(완전저장)
    - no_full : [메타데이터(class_data)를 제어하는 API]에서만 사용
        - 메타데이터 구조 전체를 보여주고 싶지 않을 때, True로 설정하면 하위 계층 메타데이터는 제거하여 반환해줌
        - Episode에서만 사용

### 4가지 API 설명
1. 전처리 데이터를 저장하는 API
    - 주소 : [IP:Port]/preprocess/json
    - 사용하는 get parameter : 없음
    1. GET : 없음
    2. POST : "전처리 서버"에서 받은 JSON 데이터로 초기 메타데이터를 생성하는 기능
        - JSON에 있는 opus 이름으로 메타데이터를 생성
        - 입력받은 season, episode 위치에 전처리 데이터를 삽입
        - 완료된 결과를 opus.origin.json에 백업하고, opus.json으로 메타데이터를 관리하도록 설정

2. 메타데이터의 구조화 변수(self.sequence_scene_shot_struct)를 제어하는 API
    - 주소 : [IP:Port]/<string:opus>/struct/json
    - 사용하는 get parameter : ?season=a&episode=b&save=False
    - 목적
        - 전처리된 이후, Frontend의 "구조화 페이지"에서 샷 경계로 나눠진 Shot들을 수기로 Scene 단위로 묶을 때 필요한 변수
        - Scene-Shot을 묶을 때는 Sequence 구조에 영향을 주지 않으므로 Sequence 단위로 구분하지 않고 scene, shot 누적번호로 관리
    - 구조화 변수의 구조
        
            - sequence_scene_shot_struct[season_num][episode_num] =
                [
                    [Scene #1의 시작 Shot 번호(누적), Scene #1의 마지막 Shot 번호(누적)],
                    [Scene #2의 시작 Shot 번호(누적), Scene #1의 마지막 Shot 번호(누적)],
                    [Scene #3의 시작 Shot 번호(누적), Scene #1의 마지막 Shot 번호(누적)],
                    [Scene #4의 시작 Shot 번호(누적), Scene #1의 마지막 Shot 번호(누적)],...
                ]
            - ex) 2개의 Sequence, 각 Sequence에 5개의 Scene, 각 Scene에 1,2,0,3,4개의 Shot이 존재
                - sequence_scene_shot_struct[0][1] = 
                [
                    [1, 1],
                    [2, 3],
                    [0, 0],
                    [4, 6],
                    [7, 10],
                    [11, 11],
                    [12, 13],
                    [0, 0],
                    [14, 16],
                    [17, 20]
                ]
                (shot이 0개인 경우가 있어서, 이 케이스에서는 [0, 0]으로 처리)
        
    1. GET
        - season=a, episode=b인 구조화 정보를 반환하는 기능
    2. POST
        - Frontend에서 가져온 season=a, episode=b의 구조화 정보를 MetadataControl 클래스에 저장
        1. save=False
            - 종료
        2. save=True
            - 저장된 Struct 변수를 기준으로 메타데이터의 Scene-Shot의 구조를 변화시킴
            - 변화시킨 구조대로 opus.json에 저장 및 임시 데이터(struct, cumulative_sum) 최신화

3. 메타데이터(self.class_data)를 제어하는 API
    - 주소 : [IP:Port]/<string:opus>/<string:class_type>/json
    - 사용하는 get parameter
        - class_type='all' : 없음
        - class_type='episode' : ?season=a&episode=b&save=False&no_full=False
        - class_type='scene' : ?season=a&episode=b&sequence=c&scene=d&save=False
        - class_type='shot' : ?season=a&episode=b&sequence=c&scene=d&shot=e&save=False
    1. GET
        1. class_type='all' : opus 단위의 전체 메타데이터를 반환
        2. class_type='episode' : episode 단위로 메타데이터를 반환하는 기능
            - no_full=False : season=a, episode=b인 Episode 메타데이터를 반환
            - no_full=True : season=a, episode=b인 메타데이터 중 sequences는 제거한 뒤 반환
        3. class_type='scene' : scene 단위로 메타데이터를 반환하는 기능
            - season=a, episode=b, sequence=c, scene=d인 Scene 메타데이터를 반환
            - 기본적으로 shots 변수는 제거되어 출력(전체 데이터 반환 기능은 X)
        4. class_type='shot' : shot 단위로 메타데이터를 반환하는 기능
            - season=a, episode=b, sequence=c, scene=d, shot=e인 Shot 메타데이터를 반환
    2. POST
        1. class_type='episode' : episode 단위의 메타데이터를 수정하는 기능
            - save=False
                - Frontend에서 보낸 값으로 MetadataControl 클래스의 episode 메타데이터를 수정
            - save=True
                - Frontend에서 보낸 값으로 MetadataControl 클래스의 episode 메타데이터를 수정한 뒤,
                - 수정된 메타데이터를 opus.json에 저장
        2. class_type='scene' : scene 단위의 메타데이터를 수정하는 기능
            - save=False
                - Frontend에서 보낸 값으로 MetadataControl 클래스의 scene 메타데이터를 수정
            - save=True
                - Frontend에서 보낸 값으로 MetadataControl 클래스의 scene 메타데이터를 수정한 뒤,
                - 수정된 메타데이터를 기준으로 sequence-scene의 구조를 변경
                - 변경된 구조대로 opus.json에 저장 및 임시 데이터(struct, cumulative_sum) 최신화
        3. class_type='shot' : shot 단위의 메타데이터를 저장
            - save=False
                - Frontend에서 보낸 값으로 MetadataControl 클래스의 shot 메타데이터를 수정
            - save=True
                - Frontend에서 보낸 값으로 MetadataControl 클래스의 shot 메타데이터를 수정한 뒤,
                - 수정된 메타데이터를 opus.json에 저장

4. Scene, Shot 누적합(self.cumulative_sum)을 return하는 API
    - 주소 : [IP:Port]/<string:opus>/total_num
    - 사용하는 get parameter : ?season=a&episode=b
    - 목적 : Episode내에서의 전체 Scene, Shot개수와 Sequence, Scene별 Scene, Shot 개수가 Frontend에서 요구되어 만든 변수
    - 누적합 변수의 구조
            
            - cumulative_sum[season_num][episode_num] = 
                [{
                    "Sequence=1의 Scene 개수":[
                        Seq=1, Scene #1의 샷 개수,
                        Seq=1, Scene #1~2의 샷 개수,
                        Seq=1, Scene #1~3의 샷 개수,
                        ...
                    ]
                },{
                    "Sequence=1~2의 Scene 개수":[
                        Seq=1의 샷 개수 + Seq=2, Scene #1의 샷 개수,
                        Seq=1의 샷 개수 + Seq=2, Scene #1~2의 샷 개수,
                        Seq=1의 샷 개수 + Seq=2, Scene #1~3의 샷 개수,
                        ...
                    ]
                }]
            - ex) 2개의 Sequence, 각 Sequence에 5개의 Scene, 각 Scene에 1,2,3,5,4개의 Shot이 존재
                - 누적합이 아닌 경우,
                    [{
                        "5":[1,2,3,5,4]
                    },{
                        "5":[1,2,3,5,4]
                    }]
                - cumulative_sum[0][1] = 
                    [{
                        "5":[1, 3, 6, 11, 15]
                    },{
                        "10":[16, 18, 21, 26, 30]
                    }]
            
    1. GET : 메타데이터의 Scene, Shot 누적합을 반환하는 기능
        1. episode != 0 : season=a, episode=b인 누적합을 반환
        2. episode == 0 : season=a인 누적합 정보를 모두 반환하는 기능
    2. POST : 없음