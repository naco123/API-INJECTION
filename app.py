from flask import Flask, request, send_file, jsonify
import os
import random
import string
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import tempfile
import subprocess

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_random_string(length=10):
    """Génère une chaîne aléatoire"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def modify_video(input_path, output_path):
    """
    Modifie la vidéo pour éviter la détection de duplication
    - Changement de métadonnées
    - Modifications visuelles légères (crop, brightness, etc.)
    """
    
    # Paramètres de modification aléatoires
    modifications = []
    
    # 1. Crop très léger (1-3 pixels de chaque côté)
    crop_top = random.randint(0, 3)
    crop_bottom = random.randint(0, 3)
    crop_left = random.randint(0, 3)
    crop_right = random.randint(0, 3)
    modifications.append(f"crop=iw-{crop_left}-{crop_right}:ih-{crop_top}-{crop_bottom}:{crop_left}:{crop_top}")
    
    # 2. Ajustement très léger de luminosité/contraste
    brightness = round(random.uniform(-0.02, 0.02), 3)
    contrast = round(random.uniform(0.98, 1.02), 3)
    modifications.append(f"eq=brightness={brightness}:contrast={contrast}")
    
    # 3. Saturation très légère
    saturation = round(random.uniform(0.98, 1.02), 3)
    modifications.append(f"eq=saturation={saturation}")
    
    # 4. Flip horizontal aléatoire (10% de chance)
    if random.random() < 0.1:
        modifications.append("hflip")
    
    # Construire le filtre video
    vf = ",".join(modifications)
    
    # 5. Changer les métadonnées
    random_title = f"Video_{generate_random_string(16)}"
    random_artist = f"Creator_{generate_random_string(10)}"
    random_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    
    # Commande ffmpeg
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vf', vf,
        '-metadata', f'title={random_title}',
        '-metadata', f'artist={random_artist}',
        '-metadata', f'date={random_date}',
        '-metadata', f'comment=Modified_{generate_random_string(20)}',
        '-metadata', f'description=Content_{generate_random_string(15)}',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'service': 'Video Metadata Modifier',
        'version': '1.0',
        'endpoints': {
            '/upload': 'POST - Upload video to modify',
            '/health': 'GET - Health check'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload et modification de vidéo
    
    Usage:
    curl -X POST -F "video=@video.mp4" http://localhost:5000/upload --output modified_video.mp4
    """
    
    # Vérifier qu'un fichier est présent
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: mp4, mov, avi'}), 400
    
    try:
        # Sauvegarder le fichier uploadé
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_id = generate_random_string(8)
        
        input_filename = f"{timestamp}_{random_id}_{filename}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        
        output_filename = f"modified_{input_filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        file.save(input_path)
        
        print(f"📥 File uploaded: {input_path}")
        
        # Modifier la vidéo
        print(f"🔄 Processing video...")
        success = modify_video(input_path, output_path)
        
        if not success:
            # Nettoyer
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': 'Video processing failed'}), 500
        
        print(f"✅ Video processed: {output_path}")
        
        # Nettoyer le fichier input
        os.remove(input_path)
        
        # Retourner le fichier modifié
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='video/mp4'
        )
        
        # Nettoyer le fichier output après envoi
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"🗑️  Cleaned up: {output_path}")
            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/batch', methods=['POST'])
def batch_upload():
    """
    Upload multiple videos at once
    Returns a ZIP file with all modified videos
    """
    # TODO: Implement batch processing if needed
    return jsonify({'error': 'Batch processing not yet implemented'}), 501

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
