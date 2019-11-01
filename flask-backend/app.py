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


@app.route('/all', methods=['GET'])
def test_get_all():
    # framework = mongo.db.framework
    #
    # output = []
    #
    # for q in framework.find():
    #     output.append({'name': q['name'], 'beds': q['beds']})
    #
    # return jsonify({'result': output})
    return "get"


@app.route('/insert_sample', methods=['POST'])
def insert_sample_entity():
    """
    insert entity api calls
    :return:
    """
    # var = {"_id": 1, "name": "wys", "score": 5}
    # collection.insert_one(var)
    for it in data:
        collection.insert_one(it)
    return 'added'


@app.route('/delete/<input_id>', methods=['DELETE'])
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


@app.route('/search/name/<item_name>', methods=['GET'])
def search_item(item_name):
    """
    search items by item name
    :param item_name:
    :return:
    """
    # find all item with same item_name
    results = collection.find({'name': item_name})

    # parse all user into json
    all_found = [{
        '_id': result['_id'],
        'name': result['name'],
        'score': result['score']
    } for result in results]

    return jsonify(all_found)


@app.route('/search/all', methods=['POST'])
def list_all():
    """
    list all data in our database
    :return:
    """
    return "all json data from data base"


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
