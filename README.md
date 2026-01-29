# Video Metadata Modifier API

API pour modifier les métadonnées et le contenu des vidéos afin d'éviter la détection de duplication sur Instagram.

## 🚀 Déploiement sur Railway

### Étapes :

1. **Créer un nouveau projet sur Railway**
   - Va sur https://railway.app
   - Clique sur "New Project"
   - Choisis "Deploy from GitHub repo"

2. **Upload ces fichiers sur ton repo GitHub**
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `railway.json`
   - `nixpacks.toml`

3. **Configurer Railway**
   - Railway détectera automatiquement le projet Python
   - FFmpeg sera installé automatiquement via nixpacks.toml
   - L'application démarrera sur le port assigné par Railway

4. **Obtenir l'URL**
   - Railway te donnera une URL type : `https://your-app.up.railway.app`

## 📝 Utilisation de l'API

### Endpoint principal : `/upload`

**Méthode :** `POST`

**Usage avec cURL :**
```bash
curl -X POST -F "video=@video.mp4" https://your-app.up.railway.app/upload --output modified_video.mp4
```

**Usage avec Python :**
```python
import requests

url = "https://your-app.up.railway.app/upload"
files = {'video': open('video.mp4', 'rb')}

response = requests.post(url, files=files)

if response.status_code == 200:
    with open('modified_video.mp4', 'wb') as f:
        f.write(response.content)
    print("✅ Video modifiée téléchargée!")
else:
    print(f"❌ Erreur: {response.json()}")
```

**Usage avec JavaScript (Node.js) :**
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('video', fs.createReadStream('video.mp4'));

axios.post('https://your-app.up.railway.app/upload', form, {
    headers: form.getHeaders(),
    responseType: 'stream'
}).then(response => {
    response.data.pipe(fs.createWriteStream('modified_video.mp4'));
    console.log('✅ Video modifiée téléchargée!');
}).catch(error => {
    console.error('❌ Erreur:', error.message);
});
```

## 🎯 Modifications appliquées

L'API applique plusieurs modifications pour rendre chaque vidéo unique :

### 1. **Métadonnées**
- Titre aléatoire
- Artiste aléatoire
- Date aléatoire (dans les 365 derniers jours)
- Commentaire aléatoire
- Description aléatoire

### 2. **Modifications visuelles légères** (imperceptibles à l'œil nu)
- Crop de 1-3 pixels sur les bords
- Ajustement de luminosité (-2% à +2%)
- Ajustement de contraste (98% à 102%)
- Ajustement de saturation (98% à 102%)
- Flip horizontal (10% de chance)

## 🔍 Endpoints disponibles

### `GET /`
Informations sur l'API

### `GET /health`
Health check de l'API

### `POST /upload`
Upload et modification d'une vidéo

**Formats acceptés :**
- MP4
- MOV
- AVI

**Taille max :** 500MB

## ⚙️ Variables d'environnement

Aucune variable d'environnement n'est nécessaire. Railway configure automatiquement `PORT`.

## 🛠️ Développement local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python app.py

# L'API sera disponible sur http://localhost:5000
```

## 📊 Limites

- Taille max par fichier : 500MB
- Timeout de traitement : 5 minutes
- Workers : 2 (configurable dans Procfile)

## ⚠️ Notes importantes

- Les fichiers sont automatiquement supprimés après traitement
- Chaque modification est unique grâce à la randomisation
- Les modifications visuelles sont imperceptibles mais suffisantes pour bypasser la détection

## 🔐 Sécurité

- Pas d'authentification par défaut (ajoute-en si besoin)
- Les fichiers temporaires sont nettoyés automatiquement
- Pas de logs persistants des uploads

## 📞 Support

Si tu as des questions ou besoin d'ajustements, contacte-moi.
