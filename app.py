from flask import Flask, request, send_file, jsonify
import os
import random
import string
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import subprocess
import uuid

app = Flask(__name__)

# Configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_string(length=12):
    """Génère une chaîne aléatoire"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def modify_video(input_path, output_path):
    """
    Modifie la vidéo pour éviter la détection de duplication Instagram
    """
    
    # Paramètres aléatoires pour chaque modification
    crop_top = random.randint(1, 4)
    crop_bottom = random.randint(1, 4)
    crop_left = random.randint(1, 4)
    crop_right = random.randint(1, 4)
    
    brightness = round(random.uniform(-0.03, 0.03), 4)
    contrast = round(random.uniform(0.97, 1.03), 4)
    saturation = round(random.uniform(0.97, 1.03), 4)
    
    # Filtres vidéo
    filters = [
        f"crop=iw-{crop_left}-{crop_right}:ih-{crop_top}-{crop_bottom}:{crop_left}:{crop_top}",
        f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"
    ]
    
    # 20% de chance de flip horizontal
    if random.random() < 0.2:
        filters.append("hflip")
    
    # 10% de chance de rotation légère
    if random.random() < 0.1:
        angle = random.uniform(-0.5, 0.5)
        filters.append(f"rotate={angle}:c=black")
    
    vf = ",".join(filters)
    
    # Métadonnées aléatoires
    metadata = {
        'title': f'Video_{random_string(20)}',
        'artist': f'Creator_{random_string(15)}',
        'comment': f'Modified_{random_string(25)}',
        'description': f'Content_{random_string(20)}',
        'date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    }
    
    # Commande FFmpeg
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vf', vf,
        '-metadata', f'title={metadata["title"]}',
        '-metadata', f'artist={metadata["artist"]}',
        '-metadata', f'comment={metadata["comment"]}',
        '-metadata', f'description={metadata["description"]}',
        '-metadata', f'date={metadata["date"]}',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', str(random.randint(22, 24)),
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg timeout après 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

@app.route('/')
def index():
    return jsonify({
        'service': 'Instagram Video Modifier',
        'version': '2.0',
        'status': 'online',
        'description': 'Modifie les métadonnées et le contenu des vidéos pour éviter la détection de duplication sur Instagram',
        'endpoints': {
            '/upload': 'POST - Upload une vidéo à modifier',
            '/health': 'GET - Health check'
        },
        'usage': {
            'curl': 'curl -X POST -F "video=@video.mp4" https://your-url.railway.app/upload -o modified.mp4',
            'formats': ['mp4', 'mov', 'avi', 'mkv'],
            'max_size': '500MB'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/upload', methods=['POST'])
def upload():
    """Upload et modification de vidéo"""
    
    if 'video' not in request.files:
        return jsonify({'error': 'Aucun fichier vidéo fourni'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Format de fichier invalide',
            'formats_acceptés': list(ALLOWED_EXTENSIONS)
        }), 400
    
    try:
        # Créer les dossiers temporaires
        temp_dir = '/tmp/video_processor'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Générer des noms de fichiers uniques
        unique_id = str(uuid.uuid4())
        input_path = os.path.join(temp_dir, f'input_{unique_id}.mp4')
        output_path = os.path.join(temp_dir, f'output_{unique_id}.mp4')
        
        # Sauvegarder le fichier uploadé
        file.save(input_path)
        file_size = os.path.getsize(input_path)
        
        print(f"📥 Fichier reçu: {file.filename} ({file_size / 1024 / 1024:.2f} MB)")
        
        # Modifier la vidéo
        print(f"🔄 Traitement en cours...")
        success = modify_video(input_path, output_path)
        
        if not success:
            # Nettoyer
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': 'Échec du traitement vidéo'}), 500
        
        print(f"✅ Vidéo modifiée avec succès")
        
        # Préparer la réponse
        output_filename = f"modified_{secure_filename(file.filename)}"
        
        def cleanup():
            """Nettoie les fichiers temporaires après l'envoi"""
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
                print(f"🗑️  Fichiers nettoyés")
            except Exception as e:
                print(f"⚠️  Erreur de nettoyage: {e}")
        
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='video/mp4'
        )
        
        response.call_on_close(cleanup)
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
