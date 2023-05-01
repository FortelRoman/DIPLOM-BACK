from flask_restful import Api, Resource
from parse import devbyParse
from mongo import addItem, getList, deleteItem, getItem, findUserByUserName, addUser
from datetime import date
import hashlib
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from flask_cors import CORS

# pip install flask flask_restful flask_cors pymongo selenium

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
api = Api()
api.init_app(app)

@app.route("/api/auth/register", methods=["POST"])
def register():
    new_user = request.get_json()
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()
    new_user["isAdmin"] = False
    doc = findUserByUserName(new_user["username"])
    if not doc:
        addUser(new_user)
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'Username already exists'}), 409


@app.route("/api/auth/login", methods=["POST"])
def login():
    login_details = request.get_json()
    user_from_db = findUserByUserName(login_details['username'])
    if user_from_db:
        encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['username'])
            refresh_token = create_refresh_token(identity=user_from_db['username'])
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return jsonify({'msg': 'The username or password is incorrect'}), 401


@app.route("/api/auth/profile", methods=["GET"])
@jwt_required(fresh=False)
def profile():
    current_user = get_jwt_identity()
    user_from_db = findUserByUserName(current_user)
    if user_from_db:
        del user_from_db['_id'], user_from_db['password']
        return jsonify({'profile': user_from_db}), 200
    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/dev-by", methods=["GET"])
@jwt_required(fresh=False)
def getResources():
    cursor = getList()
    data = [record for record in cursor]

    arr = []

    for item in data:
        print(len(item['records']))
        arr.append({
            '_id': item['_id'],
            'records': len(item['records']),
            'date': item['date'],
            'resource': item['resource'],
        })
    arr.reverse()

    return arr

@app.route("/api/dev-by", methods=["POST"])
@jwt_required(fresh=False)
def addResource():
    addItem(request.json['date'], request.json['file'])
    return jsonify({'msg': 'success'}), 200

@app.route("/api/dev-by/<id>", methods=["GET"])
@jwt_required(fresh=False)
def getResource(id):
    return getItem(id), 200

@app.route("/api/dev-by/<id>", methods=["DELETE"])
@jwt_required(fresh=False)
def deleteResource(id):
    deleteItem(id)
    return jsonify({'msg': 'success'}), 200

@app.route("/api/dev-by/parse", methods=["GET"])
@jwt_required(fresh=False)
def parseResource():
    return {'date': str(date.today()), 'records': devbyParse()}


if __name__ == "__main__":
    app.run(debug=True, port=4000)
