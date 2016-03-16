import os
import time

from flask import Flask, request, render_template, redirect, url_for, make_response, json
import facebook
import instagram
import foursquare
from github import GitHub
import requests

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

    fb_access_token = request.cookies.get('fb_access_token')
    ig_access_token = request.cookies.get('ig_access_token')
    gh_access_token = request.cookies.get('gh_access_token')
    fsq_access_token = request.cookies.get('fsq_access_token')

    services_logged_in['fb'] = fb_access_token != None
    services_logged_in['ig'] = ig_access_token != None
    services_logged_in['gh'] = gh_access_token != None
    services_logged_in['fsq'] = fsq_access_token != None

    should_show_traces = reduce(lambda a, b: a or b, services_logged_in.values(), False)

    return render_template('index.html', auth_uris=auth_uris, services_logged_in=services_logged_in, should_show_traces=should_show_traces)

"""
Login callbacks
"""
@app.route('/fb_login')
def fb_login_callback():
    fb_access_token = request.args.get('access_token')
    print("Short lived token: " + fb_access_token)


    fb_exchange_token_uri = FACEBOOK_TOKEN_EXCHANGE_URI % (
        FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET, fb_access_token
        )

    print fb_exchange_token_uri

    r = requests.get(fb_exchange_token_uri).text
    print("response " + r)
    long_lived_token = [parm for parm in r.split('&') if parm.startswith('access_token')][0][13:]
    print("Long lived token: " + long_lived_token)

    resp = make_response(redirect('/'))
    resp.set_cookie('fb_access_token', long_lived_token)

    return resp


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
@app.route('/fb_data')
def get_fb_data():
    fb_access_token = request.cookies.get('fb_access_token')

    fb = facebook.GraphAPI(fb_access_token)

    # Query user posts
    posts = fb.get_object('me/posts')

    created_ats = [post['created_time'] for post in posts['data']]
    next_ = posts['paging']['next']

    counter = 1
    while next_ != None and counter < 25:
        posts = requests.get(next_).json()
        created_ats.extend([post['created_time'] for post in posts['data']])
        next_ = posts['paging']['next']
        counter += 1

    # Query user likes
    likes = fb.get_object('me/likes')

    created_ats.extend([like['created_time'] for like in likes['data']])
    next_ = likes['paging']['next']

    counter = 1
    while next_ != None and counter < 20:
        likes = requests.get(next_).json()
        created_ats.extend([like['created_time'] for like in likes['data']])
        next_ = likes['paging']['next']
        counter += 1

    timestamps = []
    for ca in created_ats:
        ts = time.strptime(ca, "%Y-%m-%dT%H:%M:%S+0000")
        timestamps.append(ts.tm_hour * 60 + ts.tm_min)

    print("FB: " + str(len(timestamps)))

    return json.dumps(timestamps)


@app.route('/ig_data')
def get_ig_data():
    ig_access_token = request.cookies.get('ig_access_token')
    ig = instagram.client.InstagramAPI(access_token=ig_access_token, client_secret=INSTAGRAM_CLIENT_SECRET)


    all_media, next_ = ig.user_recent_media()

    created_ats = [str(m.created_time) for m in all_media]

    timestamps = []
    for ca in created_ats:
        ts = time.strptime(ca, "%Y-%m-%d %H:%M:%S")
        timestamps.append(ts.tm_hour * 60 + ts.tm_min)

    print("IG: " + str(len(timestamps)))

    return json.dumps(timestamps)

@app.route('/gh_data')
def get_gh_data():
    gh_access_token = request.cookies.get('gh_access_token')
    gh = GitHub(access_token=gh_access_token)

    user_id = gh.user().get()['login']
    page = 1
    events = gh.users(user_id).events().get(page=page)

    while True:
        page += 1        
        new_events = gh.users(user_id).events().get(page=page)
        if len(new_events) > 0:
            events.extend(new_events)
        else:
            break

    created_ats = [e['created_at'][:-1] for e in events]

    timestamps = []
    for ca in created_ats:
        ts = time.strptime(ca, "%Y-%m-%dT%H:%M:%S")
        timestamps.append(ts.tm_hour * 60 + ts.tm_min)

    print("GH: " + str(len(timestamps)))

    return json.dumps(timestamps)

@app.route('/fsq_data')
def get_fsq_data():
    fsq_access_token = request.cookies.get('fsq_access_token')
    fsq_client.set_access_token(fsq_access_token)

    checkins = fsq_client.users.checkins(params={'limit': 300})
    created_ats = [c['createdAt'] for c in checkins['checkins']['items']]
    offsets = [c['timeZoneOffset'] * 60 for c in checkins['checkins']['items']]

    timestamps = []
    for (ca, offset) in zip(created_ats, offsets):
        ts = time.gmtime(ca + offset)
        timestamps.append(ts.tm_hour * 60 + ts.tm_min)

    print("FSQ: " + str(len(timestamps)))

    return json.dumps(timestamps)

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
