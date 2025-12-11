import requests
import urllib.parse
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, redirect, request, session, render_template
from datetime import datetime
import time
from flask_apscheduler import APScheduler
from celery import Celery
from celery import shared_task
from celery.schedules import crontab

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'ania'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///User.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

CLIENT_ID = '8174df7164fc48bd9568f1766d54b0a8'
CLIENT_SECRET = 'd389cea99e3b4436bdf741e5b131246f'
REDIRECT_URI = 'http://185.237.14.36:8000/callback'
API_BASE_URL = 'https://api.spotify.com/v1/'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
AUTH_URL = 'https://accounts.spotify.com/authorize'

db = SQLAlchemy(app)
scheduler = APScheduler()
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend="redis://localhost:6379/0",
        broker="redis://localhost:6379/0"
    )


    celery.conf.update(app.config)
    '''
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    '''
    return celery

celery = make_celery(app)
#celery.config_from_object(app)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(900))
    refresh_token = db.Column(db.String(900))
    expires_at = db.Column(db.Float)    
    username = db.Column(db.String(80))
    profile_pic = db.Column(db.String(200))
    song1 = db.Column(db.String(80))
    song2 = db.Column(db.String(80))
    song3 = db.Column(db.String(80))
    song4 = db.Column(db.String(80))
    song1_img =db.Column(db.String(200))
    song2_img =db.Column(db.String(200))
    song3_img =db.Column(db.String(200))
    song4_img =db.Column(db.String(200))   
    song1art = db.Column(db.String(80))
    song2art = db.Column(db.String(80))
    song3art = db.Column(db.String(80))
    song4art = db.Column(db.String(80))


    '''
    def __init__(
            self,
            #id, 
            username,
            profile_pic,
            song1,
            song2,
            song3,
            song4,
            song1_img,
            song2_img,
            song3_img,
            song4_img,
            song1art,
            song2art, 
            song3art, 
            song4art,
            access_token, 
            refresh_token,
        ):

        #self.id = id
        self.username=username
        self.profile_pic=profile_pic
        self.song1=song1         
        self.song2=song2
        self.song3=song3
        self.song4=song4  
        self.song1_img=song1_img
        self.song2_img=song2_img
        self.song3_img=song3_img
        self.song4_img=song4_img
        self.song1art=song1art
        self.song2art=song2art
        self.song3art=song3art
        self.song4art=song4art 
        self.access_token=access_token
        self.refresh_token=refresh_token 
    '''




@app.route('/')

def index():
    return render_template("index.html")
    #return "Recent spotify plays <a href='/login'>Login with spotify</a>"

@app.route('/login')

def login():
    scope = "user-read-email, user-read-recently-played, user-read-private"

    parameters = {
        'response_type': 'code',
        'client_id': CLIENT_ID, 
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    auth_url =f"{AUTH_URL}?{urllib.parse.urlencode(parameters)}"

    return redirect(auth_url)

@app.route('/callback')

def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args["error"]})

    if 'code' in request.args:
        req_body ={
            'grant_type': 'authorization_code',
            'code': request.args['code'],
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        response = requests.post(TOKEN_URL, data=req_body)

        
        token_info = response.json()
        

        #return f"{response.json()['access_token']}"

        access_token = token_info['access_token']
        refresh_token= token_info['refresh_token']
        expires_at = datetime.now().timestamp() +token_info['expires_in']

        headers = {
           # 'Authorization': f"Bearer {session['access_token']}",
            'Authorization': f"Bearer {access_token}",
        
        }

        userData = requests.get(API_BASE_URL +'me', headers=headers).json()
        recently_played_tracks = requests.get(API_BASE_URL+'me/player/recently-played?limit=4', headers=headers).json()

        artists_name = []
        track_name = []
        img_url = []
        username = userData['display_name']

        if userData['images'] != []:
            profilepic = userData['images'][0]['url']
        else:
            profilepic="https://static-00.iconduck.com/assets.00/spotify-icon-1024x1024-7zm2z9zz.png"

        for x in range (4):
            artists_name.append(recently_played_tracks['items'][x]['track']['artists'][0]['name'])
            track_name.append(recently_played_tracks['items'][x]['track']['name'])
            img_url.append(recently_played_tracks['items'][x]['track']['album']['images'][0]['url'])

        if  User.query.filter_by(username=username).first():
            return redirect('/recent_track')

        user = User(
            access_token = access_token,
            refresh_token = refresh_token,
            expires_at = expires_at,
            username=username,
            profile_pic=profilepic,
            song1 = track_name[0],
            song2 = track_name[1],
            song3 = track_name[2],
            song4 = track_name[3],
            song1_img =img_url[0],
            song2_img =img_url[1],
            song3_img =img_url[2],
            song4_img =img_url[3],
            song1art = artists_name[0], 
            song2art = artists_name[1],
            song3art = artists_name[2], 
            song4art = artists_name[3]    
        )

        db.session.add(user)
        db.session.commit()
        return redirect('/recent_track')

@celery.task(name='recent_tracks_for_all_users')
def recent_tracks_for_all_users():
    
    with app.app_context():
        users = User.query.all()
        
    
    
        print(type(users[0]))


        for user in users:
            if datetime.now().timestamp() > user.expires_at:
                req_body ={
                    'grant_type': 'refresh_token',
                    'refresh_token': user.refresh_token,
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET
                }

                new_token_info = requests.post(TOKEN_URL, data=req_body).json()
            

                user.access_token = new_token_info['access_token']
                #user.refresh_token = new_token_info['refresh_token']
                user.expires_at = datetime.now().timestamp() + new_token_info['expires_in']

            headers={
                'Authorization': f"Bearer {user.access_token}"
            }
            updated_info = requests.get(API_BASE_URL+'me/player/recently-played?limit=4', headers=headers).json()

            artists_name = []
            track_name = []
            img_url = []

            for x in range (4):
                artists_name.append(updated_info['items'][x]['track']['artists'][0]['name'])
                track_name.append(updated_info['items'][x]['track']['name'])
                img_url.append(updated_info['items'][x]['track']['album']['images'][0]['url'])

            
            #update the current data 
            user.song1 = track_name[0]
            user.song2 = track_name[1]
            user.song3 = track_name[2]
            user.song4 = track_name[3]
            user.song1_img =img_url[0]
            user.song2_img =img_url[1]
            user.song3_img =img_url[2]
            user.song4_img =img_url[3]
            user.song1art = artists_name[0]
            user.song2art = artists_name[1]
            user.song3art = artists_name[2]
            user.song4art = artists_name[3]

            db.session.commit()
    
celery.conf.update(app.config)
celery.conf.beat_schedule = {
    'fetch-recent-tracks-every-30-seconds': {
        'task': 'recent_tracks_for_all_users',
        'schedule': 30.0,  # Co 10 sekund
    },
}   

            


@app.route('/recent_track')
def get_recent_track():
    #recent_tracks_for_all_users.delay()
    return render_template("results2.html", values = User.query.all())   

@app.route('/refresh_token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body ={
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
    
        return redirect('/recent_track')




    



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    #scheduler.add_job(id="users", func=get_recent_track, trigger='interval', seconds =5)
    #scheduler.start()
    app.run(host='0.0.0.0', port=8000)

    #use_reloader=False
