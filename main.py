from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import pandas as pd
from parse import devbyParse
from mongo import addToDataBase
import json

# pip install flask flask_restful flask_cors pymongo
# pip install pymongo[srv]

app = Flask(__name__)
CORS(app)
api = Api()

courses = {
    1: {"name": "Python", "videos": 15},
    2: {"name": "Java", "videos": 10}
}

parser = reqparse.RequestParser()
parser.add_argument("name", type=str)
parser.add_argument("videos", type=int)


class Main(Resource):
    def get(self):
        data = devbyParse()
        addToDataBase(data)
        return data
        # if course_id == 0:
        #     return parse()
        # else:
        #     return courses[course_id]

    # def delete(self, course_id):
    #     del courses[course_id]
    #     return courses
    #
    def post(self):
        # file = request.json.get('test')
        # file = request.data
        file = request.files['file']
        print(file)
        # current_data = pd.read_json(record)
        # print(current_data)
        return 'success'

    # def put(self, course_id):
    #     courses[course_id] = parser.parse_args()
    #     return courses


api.add_resource(Main, "/api/dev-by")
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=4000)
