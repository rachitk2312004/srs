from flask import Flask, render_template, request, redirect, url_for
import os
import random
from deepface import DeepFace
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg'}

SPOTIPY_CLIENT_ID = '58cecd9c163242759ca716715e530d54'
SPOTIPY_CLIENT_SECRET = '88adb1584e714a398fd9b6860b68ed41'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendation')
def recommendation():
    return render_template('recommendation.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    language = request.form.get('typesongs') 

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        try:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            emotion = detect_emotion(filename)
            
            image_url = url_for('static', filename=f'uploads/{file.filename}')
            
            recommended_songs = recommend_songs(emotion, language)
            
            return render_template('recommendation.html', filename=file.filename, emotion=emotion, image_url=image_url, recommended_songs=recommended_songs)
        except Exception as e:
            print(f"Error during upload, emotion detection, or song recommendation: {e}")
            return render_template('recommendation.html', error="An error occurred during emotion detection or song recommendation.")
    else:
        return redirect(request.url)

def detect_emotion(image_path):
    try:
        result = DeepFace.analyze(image_path)
        emotion = result['dominant_emotion']
        return emotion
    except Exception as e:
        print(f"Error during emotion detection: {e}")
        return "Unknown"

def recommend_songs(emotion, language):
    results = sp.search(q=f"mood:{emotion} language:{language}", type='track', limit=50)

    recommended_songs = []

    random.shuffle(results['tracks']['items'])
    for track in results['tracks']['items'][:20]:
        recommended_songs.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'uri': track['uri']
        })

    return recommended_songs

if __name__ == '__main__':
    app.run(debug=True)
