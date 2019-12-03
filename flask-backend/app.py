import json

from flask import Flask, render_template, jsonify, request, abort
from pymongo import MongoClient
from flaskext.mysql import MySQL
import os
import pymongo
import ssl

app = Flask(__name__)

# getting sample json file
with open('/Users/zhekunz2/Documents/cs411/thrifty/flask-backend/data/entity_sample.json',
          encoding='utf-8') as json_file:
    data = json.load(json_file)

# MongoDB configuration

# setting up mongo client uri
cluster = MongoClient("mongodb://cs411thrifty:tfsat1102200@cluster0-shard-00-00-psdci.mongodb.net:27017,"
                      "cluster0-shard-00-01-psdci.mongodb.net:27017,"
                      "cluster0-shard-00-02-psdci.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0"
                      "&authSource=admin&retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)

# setting up database and collection
db = cluster["thrifty"]
Entity = db["Entity"]
WatchHistory = db["WatchHistory"]

# Mysql Database configuration
mysql = MySQL()
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Zzk*980515'
app.config['MYSQL_DATABASE_DB'] = 'thrifty'
app.config['MYSQL_DATABASE_HOST'] = 'cs411.cnbpsgbaoain.us-east-2.rds.amazonaws.com'
mysql.init_app(app)


@app.route('/')
def index():
    return render_template("index.html", token="hello flask react")



@app.route('/thrifty/api/v1.0/entity/insert_one', methods=['POST'])
def insert_one_entity():
    """
    insert entity api call
    :return:
    """
    Entity.insert_one(request.json)
    return jsonify(request.json)



@app.route('/thrifty/api/v1.0/entity/delete/<input_id>', methods=['DELETE'])
def delete_entity(input_id):
    """
    delete entity by id
    :return:
    """

    result = Entity.find_one({"_id": input_id})
    Entity.delete_one({"_id": input_id})
    ret = {
        "_id": result["_id"],
        "name": result["name"],
        "contact": result["contact"],
        "area": result["area"],
        "description": result["description"],
        "seller": result["seller"],
        "condition": result["condition"],
        "price": result["price"],
        "date": result["date"]
    }
    return ret


@app.route('/thrifty/api/v1.0/entity/search', methods=['GET'])
def search_item_by_attr():
    """
    search items by item name, need to pass a json body
    :return:
    """

    # TODO implement multi filter
    key = ""
    for k in request.json:
        key = k
    results = Entity.find({key: request.json.get(key)})
    # find all item with same attribute

    # parse all user into json
    all_found = [{
        "_id": result["_id"],
        "name": result["name"],
        "contact": result["contact"],
        "area": result["area"],
        "description": result["description"],
        "seller": result["seller"],
        "condition": result["condition"],
        "price": result["price"],
        "date": result["date"]
    } for result in results]

    return jsonify(all_found)


@app.route('/thrifty/api/v1.0/entity/display', methods=['GET'])
def list_all():
    """
    list all data in our database
    :return:
    """
    entities = Entity.find()
    all_entity = [{
        "_id": entity["_id"],
        "name": entity["name"],
        "contact": entity["contact"],
        "area": entity["area"],
        "description": entity["description"],
        "seller": entity["seller"],
        "condition": entity["condition"],
        "price": entity["price"],
        "date": entity["date"]
    } for entity in entities]

    return jsonify(all_entity)


@app.route('/thrifty/api/v1.0/entity/update', methods=['PUT'])
def update_entity_by_id():
    """
    update database in our database by _id
    :return:
    """
    # TODO implement multi filter
    for key in request.json:
        Entity.update_one({"_id": request.json.get("_id")}, {"$set": {key: request.json.get(key)}})

    return list_all()


####### mysql api calls ####################
@app.route('/thrifty/api/v1.0/users', methods=['GET'])
def get_all_users():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    data = cursor.fetchall()
    if len(data) == 0:
        return abort(404)
    ret_data = []
    for i in range(len(data)):
        temp_data = {
            "UserId": data[i][0],
            "firstname": data[i][1],
            "lastname": data[i][2],
            "email": data[i][3],
            "phone": data[i][4]
        }
        ret_data.append(temp_data)
    return jsonify(ret_data)

@app.route('/thrifty/api/v1.0/users/<email>', methods=['GET'])
def get_uid_by_email(email):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users where email=%s", email)
    data = cursor.fetchall()
    if len(data) == 0:
        return abort(404)
    ret_data = {
        "UserId": data[0][0]
    }
    return jsonify(ret_data)

@app.route('/thrifty/api/v1.0/users', methods=['POST'])
def insert_user():
    print(request.json)
    if (not request.json) or (not 'firstname' in request.json) or (not 'password' in request.json) or (
            not 'email' in request.json) \
            or (not 'lastname' in request.json):
        abort(400)
    # Updating the SQL database
    conn = mysql.connect()
    cursor = conn.cursor()
    if 'phone' in request.json:
        phone = request.json['phone']
    else:
        phone = ""
    cursor.execute("INSERT INTO Users(firstname, lastname, password, email, phone) VALUES(%s, %s, %s, %s, %s)",
                   (request.json['firstname'], request.json['lastname'], request.json['password'],
                    request.json['email'], phone))
    data = cursor.fetchall()
    # Creating the json object based on the object in the request body
    user = {
        'name': request.json['firstname'] + " " + request.json['firstname'],
        'email': request.json['email'],
        'password': request.json['password']
    }
    conn.commit()
    conn.close()
    return jsonify({'user': user}), 201


# Getting information for a user
@app.route('/thrifty/api/v1.0/users/<uid>', methods=['GET'])
def get_user(uid):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE id=%s", uid)
    data = cursor.fetchall()
    if len(data) == 0:
        return abort(404)
    result = {
        'id': data[0][0],
        'firstname': data[0][1],
        'lastname': data[0][2],
        'email': data[0][3],
        'password': data[0][5],
        'phone': data[0][4]
    }
    return jsonify(result)


# Updating the information of a user
@app.route('/thrifty/api/v1.0/users/<uid>', methods=['PUT'])
def update_users(uid):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE id=%s", (uid))
    data = cursor.fetchall()
    if len(data) == 0:
        abort(404)
    data = {
        'firstname': data[0][1],
        'lastname': data[0][2],
        'email': data[0][3],
        'password': data[0][5],
        'phone': data[0][4]
    }
    if (not request.json) or ((not 'password' in request.json) and (not 'email' in request.json)):
        abort(400)
    for key in request.json:
        print(key)
        if key == 'email':
            cursor.execute("UPDATE Users SET email = %s WHERE id = %s", (request.json[key], uid))
        if key == 'password':
            cursor.execute("UPDATE Users SET password = %s WHERE id = %s", (request.json[key], uid))
        if key == 'phone':
            cursor.execute("UPDATE Users SET phone = %s WHERE id = %s", (request.json[key], uid))
        data[key] = request.json[key]
    conn.commit()
    conn.close()
    return jsonify(data), 201

# check login
@app.route('/thrifty/api/v1.0/login/', methods=['POST'])
def check_login():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM Users WHERE email=%s", (request.json['email']))
    data = cursor.fetchall()
    if len(data) == 0:
        abort(404)
    if data[0][0] == request.json['password']:
        data = {
            'result': 1
        }
        return jsonify(data), 201
    data = {
        'result': 0
    }
    return jsonify(data), 201


# watchHistory
@app.route('/thrifty/api/v1.0/watch_history/', methods=['POST'])
def add_watch_history():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO WatchHistory(UserId, EntityId, date) VALUES(%s, %s, %s)",
                   (request.json['UserId'], request.json['EntityId'], request.json['date']))
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    history = {
        'UserId': request.json['UserId'],
        'EntityId': request.json['EntityId'],
        'date': request.json['date']
    }
    return jsonify(history), 201

@app.route('/thrifty/api/v1.0/watch_history/<uid>', methods=['GET'])
def get_watch_history(uid):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("Select * from WatchHistory where UserId = %s", uid)
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    ret_data = []
    for i in range(len(data)):
        temp_data = {
            "UserId": data[i][0],
            "EntityId": data[i][1],
            "date": data[i][2]
        }
        ret_data.append(temp_data)
    return jsonify(ret_data), 201

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')

## SELECT * FROM Users NATRAUL JOIN WatchHistory Where id = userid group by userid