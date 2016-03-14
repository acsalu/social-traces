import os
import time

from flask import Flask, request, render_template, redirect, url_for, make_response, json
import foursquare
from github import GitHub

from keys import *

app = Flask(__name__)


fsq_client = foursquare.Foursquare(client_id=FOURSQUARE_CLIENT_ID, client_secret=FOURSQUARE_CLIENT_SECRET, redirect_uri='http://localhost:5000/fsq_login')
fsq_auth_uri = fsq_client.oauth.auth_url()

gh_client = GitHub(client_id=GITHUB_CLIENT_ID, client_secret=GITHUB_CLIENT_SECRET)
gh_auth_uri = gh_client.authorize_url()

auth_uris = {
    'github': gh_auth_uri,
    'foursquare': fsq_auth_uri
}

@app.route('/')
def index():
    services_logged_in = {}

    gh_access_token = request.cookies.get('gh_access_token')
    fsq_access_token = request.cookies.get('fsq_access_token')

    services_logged_in['github'] = gh_access_token != None
    services_logged_in['foursquare'] = fsq_access_token != None

    should_show_traces = reduce(lambda a, b: a or b, services_logged_in.values(), False)

    return render_template('index.html', auth_uris=auth_uris, services_logged_in=services_logged_in, should_show_traces=should_show_traces)

"""
Login callbacks
"""
@app.route('/gh_login')
def gh_login_callback():
    code = request.args.get('code')
    gh_access_token = gh_client.get_access_token(code)

    resp = make_response(redirect('/'))
    resp.set_cookie('gh_access_token', gh_access_token)
    
    return resp

@app.route('/fsq_login')
def fsq_login_callback():
    code = request.args.get('code')
    fsq_access_token = fsq_client.oauth.get_token(code)

    resp = make_response(redirect('/'))
    resp.set_cookie('fsq_access_token', fsq_access_token)

    return resp

"""
Data queries
"""
@app.route('/gh_data')
def get_gh_data():
    gh_access_token = request.cookies.get('gh_access_token')
    gh = GitHub(access_token=gh_access_token)

    user_id = gh.user().get()['login']
    events = gh.users(user_id).events().get()

    createdAts = [e['created_at'][:-1] for e in events]

    timestamps = []
    for ca in createdAts:
        ts = time.strptime(ca, "%Y-%m-%dT%H:%M:%S")
        timestamps.append(ts.tm_hour * 60 + ts.tm_min)
    return json.dumps(timestamps)

@app.route('/fsq_data')
def get_fsq_data():
    fsq_access_token = request.cookies.get('fsq_access_token')
    fsq_client.set_access_token(fsq_access_token)

    checkins = fsq_client.users.checkins(params={'limit': 300})
    createdAts = [c['createdAt'] for c in checkins['checkins']['items']]
    print createdAts
    print "nowWithOffset"
    createdAts = [c['createdAt'] + c['timeZoneOffset'] * 60 for c in checkins['checkins']['items']]
    print createdAts
    timestamps = []
    for ca in createdAts:
        ts = time.gmtime(ca)
        timestamps.append(ts.tm_hour * 60 + ts.tm_min)

    return json.dumps(timestamps)

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
