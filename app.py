import os

import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
	return flask.render_template('index.html')

# @app.route('/img/<path:path>')
# def send_img(path):
# 	return flask.send_from_directory('static/img', path)

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
