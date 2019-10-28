import flask

app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template("index.html", token= "hello flask react")


@app.route('/sample', methods=['GET'])
def sample_function(p):
    return 'sample function'


if __name__ == '__main__':

    app.run(debug=True)
