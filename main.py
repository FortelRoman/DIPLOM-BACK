from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
from parse import devbyParse
from mongo import addItem, getList, deleteItem, getItem
from datetime import date

# pip install flask flask_restful flask_cors pymongo selenium

class DevByList(Resource):
    def get(self):
        cursor = getList()
        data = [record for record in cursor]

        arr = []

        for item in data:
            print(len(item['vacancies']))
            arr.append({
                '_id': item['_id'],
                'count': len(item['vacancies']),
                'date': item['date'],
            })

        return arr

    def post(self):
        addItem(request.json)


class DevBy(Resource):
    def get(self, id):
        return getItem(id)

    def delete(self, id):
        deleteItem(id)


class DevByParse(Resource):
    def get(self):
        return {'date': str(date.today()), 'vacancies': devbyParse()}


if __name__ == "__main__":
    app = Flask(__name__)
    CORS(app)
    api = Api()
    api.add_resource(DevByList, "/api/dev-by")
    api.add_resource(DevByParse, "/api/dev-by/parse")
    api.add_resource(DevBy, "/api/dev-by/<id>")
    api.init_app(app)
    app.run(debug=True, port=4000)
