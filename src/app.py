from flask import Flask, jsonify, abort, request

app = Flask(__name__)


@app.route('/')
def index():
    return "Server is running"


@app.route('/sample', methods=['GET'])
def sample_function(actor_name):
    return 'sample function'


if __name__ == '__main__':
    app.run(debug=True)
