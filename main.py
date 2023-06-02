from flask_restful import Api, Resource
from parse import devbyParse
from mongo import addItem, getList, deleteItem, getItem, findUserById, findUserByLogin, updateUserPassword, addUser, getAllUsers, getUsersInfo, deleteUserDB, updateUserRoleDB, updateUserName, updateUserLogin, deleteProfileBD
from datetime import date
import hashlib
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask import Flask, request, jsonify
from flask_jwt_extended import  JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies, set_access_cookies
from pymongo import MongoClient
from flask_cors import CORS, cross_origin

# pip install flask flask_restful flask_cors pymongo selenium

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
api = Api()
api.init_app(app)
jwt = JWTManager(app)
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=7))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

@app.route("/api/auth/register", methods=["POST"])
def register():
    new_user = request.get_json()
    username = new_user["username"]
    login = new_user["login"]
    password = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()
    role = 'USER'
    doc = findUserByLogin(new_user["login"])
    if not doc:
        addUser(username, login, password, role)
        return jsonify({'msg': 'Пользователь зарегистрирован успешно'}), 201
    else:
        return jsonify({'msg': 'Такой логин уже существует в системе'}), 409

@app.route("/api/auth/login", methods=["POST"])
def login():
    login_details = request.get_json()
    user_from_db = findUserByLogin(login_details['login'])
    if user_from_db:
        encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['password']:
            response = jsonify({"msg": "login successful"})
            access_token = create_access_token(identity={'id': user_from_db['_id'], 'login': user_from_db['login'], 'role': user_from_db['role']})
            set_access_cookies(response, access_token)
            return response, 200

    return jsonify({'msg': 'Логин или пароль неверный'}), 401

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route("/api/auth/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user_from_db = findUserById(current_user['id'])
    if user_from_db:
        del user_from_db['_id'], user_from_db['password']
        return jsonify({'profile': user_from_db}), 200
    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/auth/profile", methods=["DELETE"])
@jwt_required()
def deleteProfile():
    current_user = get_jwt_identity()
    if deleteProfileBD(current_user['id']) > 0:
        response = jsonify({"msg": "delete successful"})
        unset_jwt_cookies(response)
        return response
    return jsonify({'msg': 'Error'}), 400

@app.route("/api/profile", methods=["PUT"])
@jwt_required()
def updateProfile():
    current_user = get_jwt_identity()
    params = request.get_json()
    user_from_db = findUserById(current_user['id'])

    if user_from_db:
        if 'username' in params:
            updateUserName(current_user['id'], params['username'])
            return jsonify({'msg': 'success'}), 200
        if 'login' in params:
            doc = findUserByLogin(params["login"])
            if not doc:
                updateUserLogin(current_user['id'], params['login'])
                return jsonify({'msg': 'success'}), 200
            else:
                return jsonify({'msg': 'Пользователь с таким логином уже существует'}), 409
        if 'oldPassword' in params:
            encrpted_password = hashlib.sha256(params['oldPassword'].encode("utf-8")).hexdigest()
            if encrpted_password == user_from_db['password']:
                password = hashlib.sha256(params['password'].encode("utf-8")).hexdigest()
                updateUserPassword(current_user['id'], password)
                return jsonify({'msg': 'success'}), 200
            return jsonify({'msg': 'Старый пароль неверный'}), 400
    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/dev-by", methods=["GET"])
@jwt_required()
def getResources():
    # cursor = getList()
    # data = [record for record in cursor]
    #
    # arr = []
    #
    # for item in data:
    #     print(len(item['records']))
    #     arr.append({
    #         '_id': item['_id'],
    #         'records': len(item['records']),
    #         'date': item['date'],
    #         'resource': item['resource'],
    #     })
    # arr.reverse()
    #
    # return arr
    records = getList()
    return jsonify([record for record in records])

@app.route("/api/dev-by", methods=["POST"])
@jwt_required()
def addResource():
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN' or user_role == 'ANALYST':
        if addItem(request.json['date'], request.json['file']):
            return jsonify({'msg': 'success'}), 200
        return jsonify({'msg': 'Error'}), 400
    return jsonify({'msg': 'Method not allowed'}), 403

@app.route("/api/dev-by/<id>", methods=["GET"])
@jwt_required()
def getResource(id):
    return getItem(id), 200

@app.route("/api/dev-by/<id>", methods=["DELETE"])
@jwt_required()
def deleteResource(id):
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN' or user_role == 'ANALYST':
        if deleteItem(id) > 0:
            return jsonify({'msg': 'success'}), 200
        return jsonify({'msg': 'Error'}), 400
    return jsonify({'msg': 'Method not allowed'}), 403


@app.route("/api/dev-by/parse", methods=["GET"])
@jwt_required()
def parseResource():
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN' or user_role == 'ANALYST':
        return {'date': str(date.today()), 'records': devbyParse()}
    return jsonify({'msg': 'Method not allowed'}), 403

@app.route("/api/users", methods=["GET"])
@jwt_required()
def getUsers():
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN':
        info = getUsersInfo()
        records = getAllUsers()
        info['users'] = [record for record in records]
        info['totalCount'] = info['usersCount'] + info['analystCount'] + info['adminCount']
        return jsonify(info)

    return jsonify({'msg': 'Method not allowed'}), 403

@app.route("/api/users/<id>", methods=["DELETE"])
@jwt_required()
def deleteUser(id):
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN':
        if deleteUserDB(id) > 0:
            return jsonify({'msg': 'success'}), 200
        return jsonify({'msg': 'Error'}), 400
    return jsonify({'msg': 'Method not allowed'}), 403

@app.route("/api/users/<id>", methods=["PUT"])
@jwt_required()
def updateUserRole(id):
    user_role = get_jwt_identity()['role']
    if user_role == 'ADMIN':
        if updateUserRoleDB(id, request.json['role']) > 0:
            return jsonify({'msg': 'success'}), 200
        return jsonify({'msg': 'Error'}), 400
    return jsonify({'msg': 'Method not allowed'}), 403


if __name__ == "__main__":
    app.run(debug=True, port=4000)
