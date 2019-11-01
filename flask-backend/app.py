import json

from flask import Flask, render_template, jsonify, request, abort
from pymongo import MongoClient
from flaskext.mysql import MySQL
import os
import pymongo
import ssl

app = Flask(__name__)

# getting sample json file
with open('/Users/yusenwang/thrifty/flask-backend/data/entity_sample.json',
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
collection = db["Entity"]

# Mysql Database configuration
mysql = MySQL()
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'asdfghjkl;\''
app.config['MYSQL_DATABASE_DB'] = 'thrifty_users'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
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
    collection.insert_one(request.json)
    return jsonify(request.json)


@app.route('/thrifty/api/v1.0/entity/delete/<input_id>', methods=['DELETE'])
def delete_entity(input_id):
    """
    delete entity by id
    :return:
    """

    result = collection.find_one({"_id": input_id})
    collection.delete_one({"_id": input_id})
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
    results = collection.find({key: request.json.get(key)})
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
    entities = collection.find()
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
        collection.update_one({"_id": request.json.get("_id")}, {"$set": {key: request.json.get(key)}})

    return list_all()


# mysql api calls
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
            "name": data[i][1] + " " + data[i][2],
            "email": data[i][3],
            "phone": data[i][4]
        }
        ret_data.append(temp_data)
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


if __name__ == '__main__':
    app.run(debug=True)
