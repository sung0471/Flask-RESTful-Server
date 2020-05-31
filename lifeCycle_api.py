from flask import Flask, make_response, render_template
from flask_restful import Resource, Api
from library.directory_control import get_metadata_dir_path
from utils.metadata_control import MetadataControl
import json

app = Flask(__name__)
api = Api(app)

file_name = "1005.json"
file_path = get_metadata_dir_path(file_name, file_name.split('.')[0])
# data=get_data_total("1001_v3_sum.json")
metadata = MetadataControl(in_filepath=file_path)
data = metadata.get_life_cycle()


class make_to_html(Resource):
    def get(self):
        res = make_response(render_template('view_lifecycle.html'))
        res.headers['Content-type'] = 'text/html'
        return res


class make_to_json(Resource):
    def get(self):
        res = make_response(json.dumps(data, indent=2, ensure_ascii=False))
        res.headers['Content-type'] = 'application/json'
        return res


api.add_resource(make_to_html, '/html')     # 인물들의 lifecycle을 HTML 템플릿으로 출력
api.add_resource(make_to_json, '/json')     # 인물들의 lifecycle을 json 데이터로 출력


if __name__ == '__main__':
    # app.run(debug=True)        # 디버그 모드 실행
    app.run(host='0.0.0.0')     # 외부에서 접속가능한 서버로 실행
