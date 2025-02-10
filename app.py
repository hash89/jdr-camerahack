from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from math import radians, cos, sin, asin, sqrt
from flask_cors import CORS
from flask_session import Session
import os
import logging
import uuid

app = Flask(__name__)

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)

# Configuration des sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'votre_clé_secrète')  # Utiliser une variable d'environnement
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session'  # Répertoire des sessions monté en volume
app.config['SESSION_PERMANENT'] = False
Session(app)

CORS(app)  # Activer CORS si nécessaire

# Définir les caméras avec des UUID et des noms uniques
CAMERAS = [
    {
        'id': str(uuid.uuid4()),
        'name': 'Caméra 1',
        'latitude': 47.3890816,
        'longitude': 0.7143424,
        'allowed_radius': 2000,  # en mètres
        'image_filename': 'cam_feed1.jpg',
        'password': 'Aucune correspondance plosible sur l\'itinéraire ouest'  # Mot de passe défini pour Caméra 1
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Caméra 2',
        'latitude': 47.3890816,
        'longitude': 0.7143424,
        'allowed_radius': 2000,
        'image_filename': 'cam_feed2.jpg',
        'password': 'Individu sur l\'itinéraire sud, repéré, ce n\'est pas la cible'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Caméra 3',
        'latitude': 47.3890816,
        'longitude': 0.7143424,
        'allowed_radius': 2000,
        'image_filename': 'cam_feed3.jpg',
        'password': 'Individu sur l\'itinéraire sud-est, repéré, il ne correspond pas'
    }
    # Ajoutez autant de caméras que nécessaire
]

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcul de la distance entre deux points géographiques en utilisant la formule de Haversine.
    Retourne la distance en mètres.
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Rayon de la Terre en mètres
    return c * r

@app.route('/')
def index():
    # Initialiser la liste des caméras débloquées dans la session
    if 'unlocked_cameras' not in session:
        session['unlocked_cameras'] = []
    unlocked_cameras = session['unlocked_cameras']
    logging.debug(f"Caméras débloquées: {unlocked_cameras}")
    return render_template('index.html', cameras=CAMERAS, unlocked_cameras=unlocked_cameras)

@app.route('/camera/<string:camera_id>')
def camera(camera_id):
    # Vérifier l'existence de la caméra
    camera = next((cam for cam in CAMERAS if cam['id'] == camera_id), None)
    if not camera:
        return "Caméra non trouvée", 404

    # Trouver l'index de la caméra actuelle
    camera_index = CAMERAS.index(camera)

    # Vérifier si les caméras précédentes sont débloquées
    if camera_index > 0:
        previous_camera_id = CAMERAS[camera_index - 1]['id']
        if previous_camera_id not in session.get('unlocked_cameras', []):
            # Rediriger vers la dernière caméra débloquée ou index si aucune
            if session['unlocked_cameras']:
                # Trouver la caméra maximale en termes d'ordre
                last_unlocked_camera_id = session['unlocked_cameras'][-1]
                last_unlocked_camera = next((cam for cam in CAMERAS if cam['id'] == last_unlocked_camera_id), None)
                if last_unlocked_camera:
                    return redirect(url_for('camera', camera_id=last_unlocked_camera['id']))
            return redirect(url_for('index'))

    # Déterminer si la caméra est déjà déverrouillée
    is_unlocked = camera_id in session.get('unlocked_cameras', [])
    camera_password = camera['password'] if is_unlocked else None

    # Passer l'index actuel et la liste des caméras pour la navigation
    return render_template('camera.html', camera=camera, cameras=CAMERAS, is_unlocked=is_unlocked, camera_password=camera_password, current_index=camera_index)

@app.route('/verify_location', methods=['POST'])
def verify_location():
    data = request.get_json()
   
    if not data or 'latitude' not in data or 'longitude' not in data or 'camera_id' not in data:
        return jsonify({'success': False, 'message': 'Données de localisation ou ID de caméra manquantes.'}), 400
   
    user_lat = data['latitude']
    user_lon = data['longitude']
    camera_id = data['camera_id']
   
    # Trouver la caméra correspondante
    camera = next((cam for cam in CAMERAS if cam['id'] == camera_id), None)
    if not camera:
        return jsonify({'success': False, 'message': 'Caméra non trouvée.'}), 404
   
    # Calculer la distance
    distance = haversine(user_lat, user_lon, camera['latitude'], camera['longitude'])
    logging.debug(f"Distance calculée pour {camera['name']}: {distance} mètres")
   
    if distance <= camera['allowed_radius']:
        # Débloquer la caméra si ce n'est pas déjà fait
        if 'unlocked_cameras' not in session:
            session['unlocked_cameras'] = []
        if camera_id not in session['unlocked_cameras']:
            session['unlocked_cameras'].append(camera_id)
            session.modified = True
            logging.debug(f"Caméra {camera_id} ajoutée aux caméras débloquées")
        return jsonify({
            'success': True,
            'message': f'Accès autorisé : Vous êtes dans la zone de la {camera["name"]}.',
            'password': camera['password']  # Renvoyer le mot de passe défini dans l'objet camera
        })
    else:
        return jsonify({'success': False, 'message': f'Accès refusé : Vous êtes hors de la zone de la {camera["name"]}.'})

@app.route('/reset')
def reset():
    # Réinitialiser la progression des caméras
    session.pop('unlocked_cameras', None)
    return redirect(url_for('index'))

@app.route('/force_unlock/<string:camera_id>')
def force_unlock(camera_id):
    if 'unlocked_cameras' not in session:
        session['unlocked_cameras'] = []
    if camera_id not in session['unlocked_cameras']:
        session['unlocked_cameras'].append(camera_id)
        session.modified = True
        logging.debug(f"Caméra {camera_id} débloquée manuellement")
    return f"Caméra {camera_id} débloquée. <a href='{url_for('index')}'>Retour à l'accueil</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)