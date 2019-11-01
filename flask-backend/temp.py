#!/usr/bin/python3

import pymongo
from flaskext.mysql import MySQL
from flask import Flask, render_template, app, jsonify, abort, make_response, request

app = Flask(__name__)

# Database configuration
mysql = MySQL()
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Zzk*980515'
app.config['MYSQL_DATABASE_DB'] = 'thrifty_users'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


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
    if (not request.json) or (not 'firstname' in request.json) or (not 'password' in request.json) or (not 'email' in request.json) \
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