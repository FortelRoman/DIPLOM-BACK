from flask_restful import Api, Resource
from parse import devbyParse
from mongo import addItem, getList, deleteItem, getItem, findUserByUserName, addUser, getAllUsers, deleteUserDB, updateUserRoleDB
from datetime import date
import hashlib
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from flask_cors import CORS

# pip install flask flask_restful flask_cors pymongo selenium

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
api = Api()
api.init_app(app)

@app.route("/api/auth/register", methods=["POST"])
def register():
    new_user = request.get_json()
    username = new_user["username"]
    password = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()
    role = 'USER'
    doc = findUserByUserName(new_user["username"])
    if not doc:
        addUser(username, password, role)
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
            access_token = create_access_token(identity={'username': user_from_db['username'], 'role': user_from_db['role']})
            # refresh_token = create_refresh_token(identity=user_from_db['username'])
            return jsonify(access_token=access_token), 200

    return jsonify({'msg': 'The username or password is incorrect'}), 401


@app.route("/api/auth/profile", methods=["GET"])
@jwt_required(fresh=False)
def profile():
    current_user = get_jwt_identity()
    user_from_db = findUserByUserName(current_user['username'])
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
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN' or user_role == 'ANALYST':
        if addItem(request.json['date'], request.json['file']):
            return jsonify({'msg': 'success'}), 200
        return jsonify({'msg': 'Error'}), 400
    return jsonify({'msg': 'Method not allowed'}), 403

@app.route("/api/dev-by/<id>", methods=["GET"])
@jwt_required(fresh=False)
def getResource(id):
    return getItem(id), 200

@app.route("/api/dev-by/<id>", methods=["DELETE"])
@jwt_required(fresh=False)
def deleteResource(id):
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN' or user_role == 'ANALYST':
        if deleteItem(id) > 0:
            return jsonify({'msg': 'success'}), 200
        return jsonify({'msg': 'Error'}), 400
    return jsonify({'msg': 'Method not allowed'}), 403


@app.route("/api/dev-by/parse", methods=["GET"])
@jwt_required(fresh=False)
def parseResource():
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN' or user_role == 'ANALYST':
        return {'date': str(date.today()), 'records': devbyParse()}
    return jsonify({'msg': 'Method not allowed'}), 403

@app.route("/api/users", methods=["GET"])
@jwt_required(fresh=False)
def getUsers():
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN':
        cursor = getAllUsers()
        data = [record for record in cursor]

        arr = []

        for item in data:
            arr.append({
                '_id': item['_id'],
                'username': item['username'],
                'role': item['role'],
            })
        arr.reverse()

        return arr
    return jsonify({'msg': 'Method not allowed'}), 403

@app.route("/api/users/<id>", methods=["DELETE"])
@jwt_required(fresh=False)
def deleteUser(id):
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN':
        if deleteUserDB(id) > 0:
            return jsonify({'msg': 'success'}), 200
        return jsonify({'msg': 'Error'}), 400
    return jsonify({'msg': 'Method not allowed'}), 403

@app.route("/api/users/<id>", methods=["PUT"])
@jwt_required(fresh=False)
def updateUserRole(id):
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN':
        if updateUserRoleDB(id, request.json['role']) > 0:
            return jsonify({'msg': 'success'}), 200
        return jsonify({'msg': 'Error'}), 400
    return jsonify({'msg': 'Method not allowed'}), 403


CORS(app)

if __name__ == "__main__":
    app.run(debug=True, port=4000)
