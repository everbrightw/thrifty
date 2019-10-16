from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():

    return "Server is running"


@app.route('/sample', methods=['GET'])
def sample_function(p):
    return 'sample function'

@app.route('/name', methods=['GET'])
def get_name(p):
    return 'sample function'


if __name__ == '__main__':
    app.run(debug=True)
