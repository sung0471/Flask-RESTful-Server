"""
Description
    Returns the frequency of each scene or episode of the characters in the video
"""

from flask import Flask, make_response, render_template
from flask_restful import Resource, Api
from library.directory_control import get_file_dir_path
from utils.metadata_control import MetadataControl
import json

template_path = get_file_dir_path('lifecycle', 'templates')
app = Flask(__name__, template_folder=template_path)
api = Api(app)

file_name = "1005.json"
file_path = get_file_dir_path(file_name, ['metadata', 'lifecycle'])
# data=get_data_total("1001_v3_sum.json")
metadata = MetadataControl(in_filepath=file_path)
data = metadata.get_life_cycle()


class LifeCycle(Resource):
    def get(self, data_type=None):
        if data_type is None:
            api_description = '<h2>LifeCycle API Description</h2>' \
                              '<table border="1" style="border-collapse:collapse">' \
                              '<tr><td>/html</td><td>인물들의 lifecycle을 HTML 템플릿으로 출력</td></tr>' \
                              '<tr><td>/json</td><td>인물들의 lifecycle을 json 데이터로 출력</td></tr>' \
                              '</table>'
            res = make_response(api_description)
            res.headers['Content-type'] = 'text/html; charset=utf-8'
        elif data_type == 'html':
            res = make_response(render_template('view_lifecycle.html'))
            res.headers['Content-type'] = 'text/html'
        else:
            res = make_response(json.dumps(data, indent=2, ensure_ascii=False))
            res.headers['Content-type'] = 'application/json'

        return res


api.add_resource(LifeCycle, '/', '/<string:data_type>')
# /html     # 인물들의 lifecycle을 HTML 템플릿으로 출력
# /json     # 인물들의 lifecycle을 json 데이터로 출력


if __name__ == '__main__':
    # app.run(debug=True)        # 디버그 모드 실행
    app.run(host='0.0.0.0')     # 외부에서 접속가능한 서버로 실행
