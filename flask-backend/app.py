import json
import re
from flask import Flask, render_template, jsonify, request, abort
from pymongo import MongoClient
from flaskext.mysql import MySQL
import os
import pymongo
import ssl
from bson import ObjectId

app = Flask(__name__)

# getting sample json file
# <<<<<<< HEAD
# with open('/Users/yusenwang/thrifty/flask-backend/data/entity_sample.json',
#           encoding='utf-8') as json_file:
#     data = json.load(json_file)
# =======
# # with open('/Users/zhekunz2/Documents/cs411/thrifty/flask-backend/data/entity_sample.json',
# #           encoding='utf-8') as json_file:
# #     data = json.load(json_file)
# >>>>>>> 86456c5b7d4b204abe7d6e248dd2b509af0523ca

# MongoDB configuration
# _id, name, price, condition, category, description, userid, date, picture
# setting up mongo client uri
cluster = MongoClient("mongodb://cs411thrifty:tfsat1102200@cluster0-shard-00-00-psdci.mongodb.net:27017,"
                      "cluster0-shard-00-01-psdci.mongodb.net:27017,"
                      "cluster0-shard-00-02-psdci.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0"
                      "&authSource=admin&retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)

# setting up database and collection
db = cluster["thrifty"]
Entity = db["Entity"]

# Mysql Database configuration
mysql = MySQL()
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Zzk*980515'
app.config['MYSQL_DATABASE_DB'] = 'thrifty'
app.config['MYSQL_DATABASE_HOST'] = 'cs411.cnbpsgbaoain.us-east-2.rds.amazonaws.com'
mysql.init_app(app)

### Advanced Function 1

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("drop trigger if exists mytrigger")
qrystr = "CREATE TRIGGER mytrigger BEFORE INSERT ON WatchHistory for each row begin IF ((select COUNT(*) from WatchHistory w where w.Entity=NEW.Entity) >= 10) and ((select COUNT(*) from Hottest h where h.EntityId=NEW.Entity)=0) THEN INSERT INTO Hottest(EntityId) VALUES(NEW.Entity); END IF; END"
cursor.execute(qrystr)
conn.commit()
conn.close()
##############

@app.route('/')
def index():
    return render_template("index.html", token="hello flask react")


# _id, name, price, condition, category, description, userid, date, picture

@app.route('/thrifty/api/v1.0/entity/insert', methods=['POST'])
def insert_one_entity():
    """
    insert entity api call
    :return:
    """
    result = request.json
    print(request.json)
    Entity.insert_one(request.json)
    ret = {
        "_id": str(result["_id"]),
        "name": result["name"],
        "userid": result["userid"],
        "description": result["description"],
        "condition": result["condition"],
        "category": result["category"],
        "price": result["price"],
        "picture": result["picture"]
    }
    return ret

@app.route('/thrifty/api/v1.0/entity/insert_many', methods=['POST'])
def insert_many_entity():
    """
    insert entity api call
    :return:
    """
    results = request.json
    data = []
    for result in results:
        Entity.insert_one(i)
        ret = {
            "_id": str(result["_id"]),
            "name": result["name"],
            "userid": result["userid"],
            "description": result["description"],
            "condition": result["condition"],
            "category": result["category"],
            "price": result["price"],
            "picture": result["picture"]
        }
        data.append(ret)
    return jsonify(data), 201


@app.route('/thrifty/api/v1.0/entity/delete/<input_id>', methods=['DELETE'])
def delete_entity(input_id):
    """
    delete entity by id
    :return:
    """
    print("delete")
    result = Entity.find_one({"_id": input_id})
    Entity.delete_one({"_id": input_id})
    ret = {
        "_id": str(result["_id"]),
        "name": result["name"],
        "userid": result["userid"],
        "description": result["description"],
        "condition": result["condition"],
        "category": result["category"],
        "price": result["price"],
        "picture": result["picture"]
    }
    return ret

@app.route('/thrifty/api/v1.0/entity/', methods=['GET'])
def get_all_entities():
    """
    search items by item name, need to pass a json body
    :return:
    """
    results = Entity.find()
    # find all item with same attribute

    # parse all user into json
    all_found = []
    for result in results:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("Select Count(*) from WatchHistory where Entity=%s", str(result["_id"]))
        data = cursor.fetchall()
        cursor.execute("Select email from Users where id=%s", result["userid"])
        user = cursor.fetchall()
        all_found.append({
            # "_id": str(result["_id"]),
            "name": result["name"],
            "email": user[0][0],
            # "userId": result["userid"],
            "description": result["description"],
            # "condition": result["condition"],
            "category": result["category"],
            "price": result["price"],
            "views": str(data[0][0])
            # "picture": result["picture"]
        })
    return jsonify(all_found)

@app.route('/thrifty/api/v1.0/entity/category/<category>', methods=['GET'])
def get_entities_by_category(category):
    """
    search items by item name, need to pass a json body
    :return:
    """
    results = Entity.find({"category":category})
    # find all item with same attribute

    # parse all user into json
    all_found = []
    for result in results:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("Select Count(*) from WatchHistory where Entity=%s", str(result["_id"]))
        data = cursor.fetchall()
        cursor.execute("Select email from Users where id=%s", int(result["userid"]))
        user = cursor.fetchall()
        all_found.append({
            # "_id": str(result["_id"]),
            "name": result["name"],
            "email": user[0][0],
            # "userId": result["userid"],
            "description": result["description"],
            # "condition": result["condition"],
            "category": result["category"],
            "price": result["price"],
            "views": str(data[0][0])
            # "picture": result["picture"]
        })
    return jsonify(all_found)

# Search
@app.route('/thrifty/api/v1.0/entity/search/<name>', methods=['GET'])
def search_item_by_name(name):
    """
    search items by item name
    :return:
    """
    regx = re.compile(".*"+name+".*", re.IGNORECASE)
    # regx = { "name": { "$regex": "*."+name+".*" } }
    results=(Entity.find({"name": regx}))
    # find all item with same attribute

    # parse all user into json
    all_found = []
    for result in results:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("Select Count(*) from WatchHistory where Entity=%s", str(result["_id"]))
        data = cursor.fetchall()
        cursor.execute("Select email from Users where id=%s", result["userid"])
        user = cursor.fetchall()
        all_found.append({
            # "_id": str(result["_id"]),
            "name": result["name"],
            "email": user[0][0],
            "description": result["description"],
            # "condition": result["condition"],
            "category": result["category"],
            "price": result["price"],
            "views": str(data[0][0])
            # "picture": result["picture"]
        })

    return jsonify(all_found)


@app.route('/thrifty/api/v1.0/entity/update', methods=['PUT'])
def update_entity_by_id():
    """
    update database in our database by _id
    :return:
    """
    # TODO implement multi filter
    for key in request.json:
        Entity.update_one({"_id": request.json.get("_id")}, {"$set": {key: request.json.get(key)}})

    return get_all_entities()


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

@app.route('/thrifty/api/v1.0/users/email/<email>', methods=['GET'])
def get_uid_by_email(email):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users where email=%s", email)
    data = cursor.fetchall()
    if len(data) == 0:
        return abort(401)
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
@app.route('/thrifty/api/v1.0/users/uid/<uid>', methods=['GET'])
def get_user_by_id(uid):
    print("heressss")
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE id=%s", uid)
    data = cursor.fetchall()
    if len(data) == 0:
        return abort(401)
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
    cursor.execute("SELECT password, id FROM Users WHERE email=%s", (request.json['email']))
    data = cursor.fetchall()
    if len(data) == 0:
        abort(404)
    if data[0][0] == request.json['password']:
        data = {
            'result': "isvalid",
            'UserId': str(data[0][1])
        }
        return jsonify(data), 201
    data = {
        'result': "notvalid"
    }
    return jsonify(data), 201


########## watchHistory

@app.route('/thrifty/api/v1.0/watch_history', methods=['POST'])
def add_watch_history():
    conn = mysql.connect()
    cursor = conn.cursor()
    result = Entity.find_one({"name": request.json['entity']})
    cursor.execute("INSERT INTO WatchHistory(UserId, Entity) VALUES(%s, %s)",
                   (request.json['userId'], str(result["_id"])))
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    history = {
        'UserId': request.json['userId'],
        'Entity': request.json['entity'],
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
            "Entity": data[i][1],
        }
        ret_data.append(temp_data)
    return jsonify(ret_data), 201

################# Favorites
########## watchHistory

# @app.route('/thrifty/api/v1.0/favorites/', methods=['POST'])
# def add_favorite():
#     conn = mysql.connect()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO Favorites(UserId, EntityId) VALUES(%s, %s)",
#                    (request.json['UserId'], request.json['EntityId']))
#     data = cursor.fetchall()
#     conn.commit()
#     conn.close()
#     history = {
#         'UserId': request.json['UserId'],
#         'EntityId': request.json['EntityId'],
#     }
#     return jsonify(history), 201

# @app.route('/thrifty/api/v1.0/favorites/<uid>', methods=['GET'])
# def get_favorites(uid):
#     conn = mysql.connect()
#     cursor = conn.cursor()
#     cursor.execute("Select * from Favorites where UserId = %s", uid)
#     data = cursor.fetchall()
#     conn.commit()
#     conn.close()
#     ret_data = []
#     for i in range(len(data)):
#         temp_data = {
#             "UserId": data[i][0],
#             "EntityId": data[i][1],
#         }
#         ret_data.append(temp_data)
#     return jsonify(ret_data), 201

# app.route('/thrifty/api/v1.0/favorites/<uid>/<eid>', methods=['DELETE'])
# def get_favorites(uid, eid):
#     conn = mysql.connect()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM Favorites WHERE UserId=%s and EntityId=%s", uid, eid)
#     data = cursor.fetchall()
#     conn.commit()
#     conn.close()
#     ret_data = {
#         "UserId": uid,
#         "EntityId": eid
#     }
#     return ret_data, 201


# Advanced Function 1 Helpper
@app.route('/thrifty/api/v1.0/hottest', methods=['GET'])
def get_hottest():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("Select EntityId from Hottest")
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    results = []
    for i in range(len(data)):
        entityId=data[i][0]
        result = Entity.find_one({"_id": ObjectId(entityId)})
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("Select Count(*) from WatchHistory where Entity=%s", str(result["_id"]))
        view = cursor.fetchall()
        cursor.execute("Select email from Users where id=%s", result["userid"])
        user = cursor.fetchall()
        results.append({
            # "_id": str(result["_id"]),
            "name": result["name"],
            "email": user[0][0],
            "description": result["description"],
            # "condition": result["condition"],
            "category": result["category"],
            "price": result["price"],
            "views": str(view[0][0])
            # "picture": result["picture"]
        })
    results.sort(key=extractView, reverse=True)
    return jsonify(results)

def extractView(json):
    try:
        return int(json['view'])
    except KeyError:
        return 0

# Advanced Function 2
@app.route('/thrifty/api/v1.0/suggestion/<uid>', methods=['GET'])
def get_suggestion(uid):
    conn = mysql.connect()
    cursor = conn.cursor()
    # "SELECT       `column`,
    #          COUNT(`column`) AS `value_occurrence` 
    # FROM     `my_table`
    # GROUP BY `column`
    # ORDER BY `value_occurrence` DESC
    # LIMIT    1;"
    cursor.execute("Select Entity, COUNT(Entity) as count from (Select * from WatchHistory where UserId = %s) s group by Entity order by count DESC LIMIT 1", uid)
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    print(data)
    all_results = []
    for i in range(len(data)):
        entityId=data[i][0]
        result = Entity.find_one({"_id": ObjectId(entityId)})
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("Select Count(*) from WatchHistory where Entity=%s", str(result["_id"]))
        view = cursor.fetchall()
        cursor.execute("Select email from Users where id=%s", result["userid"])
        user = cursor.fetchall()
        all_results.append({
            # "_id": str(result["_id"]),
            "name": result["name"],
            "email": user[0][0],
            "description": result["description"],
            # "condition": result["condition"],
            "category": result["category"],
            "price": result["price"],
            "views": str(view[0][0])
            # "picture": result["picture"]
        })
    return jsonify(all_results)


if __name__ == '__main__':
    # app.debug=True
    app.run(debug=True, host="0.0.0.0",port=8888)

## SELECT * FROM Users u JOIN WatchHistory w ON u.id = w.UserId group by EntityId