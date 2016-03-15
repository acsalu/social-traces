import os
import time

from flask import Flask, request, render_template, redirect, url_for, make_response, json
import instagram
import foursquare
from github import GitHub

from keys import *

app = Flask(__name__)


ig_client = instagram.client.InstagramAPI(client_id=INSTAGRAM_CLIENT_ID, client_secret=INSTAGRAM_CLIENT_SECRET, redirect_uri=INSTAGRAM_REDIRECT_URI)
ig_auth_url = ig_client.get_authorize_url()

fsq_client = foursquare.Foursquare(client_id=FOURSQUARE_CLIENT_ID, client_secret=FOURSQUARE_CLIENT_SECRET, redirect_uri=FOURSQUARE_REDIRECT_URI)
fsq_auth_uri = fsq_client.oauth.auth_url()

gh_client = GitHub(client_id=GITHUB_CLIENT_ID, client_secret=GITHUB_CLIENT_SECRET)
gh_auth_uri = gh_client.authorize_url()

auth_uris = {
    'ig': ig_auth_url,
    'gh': gh_auth_uri,
    'fsq': fsq_auth_uri
}

@app.route('/')
def index():
    services_logged_in = {}

    ig_access_token = request.cookies.get('ig_access_token')
    gh_access_token = request.cookies.get('gh_access_token')
    fsq_access_token = request.cookies.get('fsq_access_token')

    print ig_access_token

    services_logged_in['ig'] = ig_access_token != None
    services_logged_in['gh'] = gh_access_token != None
    services_logged_in['fsq'] = fsq_access_token != None

    should_show_traces = reduce(lambda a, b: a or b, services_logged_in.values(), False)

    return render_template('index.html', auth_uris=auth_uris, services_logged_in=services_logged_in, should_show_traces=should_show_traces)

"""
Login callbacks
"""
@app.route('/ig_login')
def ig_login_callback():
    code = request.args.get('code')
    ig_access_token, user_info = ig_client.exchange_code_for_access_token(code)

    resp = make_response(redirect('/'))
    resp.set_cookie('ig_access_token', ig_access_token)
    
    return resp


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
@app.route('/ig_data')
def get_ig_data():
    ig_access_token = request.cookies.get('ig_access_token')
    ig = instagram.client.InstagramAPI(access_token=ig_access_token, client_secret=INSTAGRAM_CLIENT_SECRET)


    all_media, next_ = ig.user_recent_media()

    createdAts = [str(m.created_time) for m in all_media]

    timestamps = []
    for ca in createdAts:
        ts = time.strptime(ca, "%Y-%m-%d %H:%M:%S")
        timestamps.append(ts.tm_hour * 60 + ts.tm_min)
    return json.dumps(timestamps)

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

    timestamps = []
    for ca in createdAts:
        ts = time.gmtime(ca)
        timestamps.append(ts.tm_hour * 60 + ts.tm_min)

    return json.dumps(timestamps)

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
