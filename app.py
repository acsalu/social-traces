import os

from flask import Flask, request, render_template, redirect, url_for, make_response, json
import foursquare

app = Flask(__name__)

FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')

fsq_client = foursquare.Foursquare(client_id=FOURSQUARE_CLIENT_ID, client_secret=FOURSQUARE_CLIENT_SECRET, redirect_uri='http://social-traces.herokuapp.com/foursquare')
fsq_auth_uri = fsq_client.oauth.auth_url()

@app.route('/')
def index():

    fsq_access_token = request.cookies.get('fsq_access_token')
    if not fsq_access_token:
        return render_template('index.html', fsq_auth_uri=fsq_auth_uri) 
    else:
        fsq_client.set_access_token(fsq_access_token)

        checkins = fsq_client.users.checkins(params={'limit': 100})
        checkins = [c['createdAt'] for c in checkins['checkins']['items']]

        return render_template('index.html', checkins=checkins)

@app.route('/foursquare')
def get_foursquare_token():
    code = request.args.get('code')
    fsq_access_token = fsq_client.oauth.get_token(code)

    resp = make_response(redirect('/'))
    resp.set_cookie('fsq_access_token', fsq_access_token)

    return resp

@app.route('/foursquare_data')
def get_foursquare_data():
    fsq_access_token = request.cookies.get('fsq_access_token')

    checkins = fsq_client.users.checkins(params={'limit': 100})
    checkins = [c['createdAt'] for c in checkins['checkins']['items']]
    print checkins
    return json.dumps(checkins)

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
