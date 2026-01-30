# 🎥 Instagram Video Modifier API

API Flask pour modifier les métadonnées et le contenu des vidéos afin d'éviter la détection de duplication sur Instagram.

## 🎯 Pourquoi ce bot ?

Instagram détecte les vidéos dupliquées et peut :
- Réduire la portée organique
- Bloquer la publication sur plusieurs comptes
- Marquer le contenu comme spam

Ce bot modifie **subtilement** chaque vidéo pour qu'Instagram la considère comme unique.

## ✨ Modifications appliquées

### 1️⃣ Métadonnées aléatoires
- Titre unique
- Artiste unique
- Date aléatoire
- Commentaire unique
- Description unique

### 2️⃣ Modifications visuelles imperceptibles
- **Crop** : 1-4 pixels sur chaque bord (aléatoire)
- **Luminosité** : -3% à +3% (aléatoire)
- **Contraste** : 97% à 103% (aléatoire)
- **Saturation** : 97% à 103% (aléatoire)
- **Flip horizontal** : 20% de chance
- **Rotation légère** : 10% de chance (-0.5° à +0.5°)
- **CRF** : 22-24 (qualité variable)

**Résultat** : Chaque vidéo est techniquement différente mais visuellement identique ! 👌

## 🚀 Déploiement sur Railway

### Étape 1 : Préparer ton repo GitHub

1. Crée un nouveau repo sur GitHub
2. Upload ces fichiers :
   - `app.py`
   - `requirements.txt`
   - `nixpacks.toml`
   - `.gitignore`
   - `README.md`

### Étape 2 : Déployer sur Railway

1. Va sur [railway.app](https://railway.app)
2. Clique sur **"New Project"**
3. Sélectionne **"Deploy from GitHub repo"**
4. Choisis ton repo
5. Railway va :
   ✅ Détecter Python automatiquement
   ✅ Installer FFmpeg via nixpacks.toml
   ✅ Installer les dépendances Python
   ✅ Lancer l'API

### Étape 3 : Obtenir ton URL

Railway te donnera une URL type :
```
https://ton-projet.up.railway.app
```

## 📡 Utilisation de l'API

### Endpoint principal : `POST /upload`

#### Avec cURL
```bash
curl -X POST \
  -F "video=@ma_video.mp4" \
  https://ton-projet.up.railway.app/upload \
  -o video_modifiee.mp4
```

#### Avec Python
```python
import requests

url = "https://ton-projet.up.railway.app/upload"
files = {'video': open('ma_video.mp4', 'rb')}

response = requests.post(url, files=files)

if response.status_code == 200:
    with open('video_modifiee.mp4', 'wb') as f:
        f.write(response.content)
    print("✅ Vidéo modifiée !")
else:
    print(f"❌ Erreur: {response.json()}")
```

#### Avec JavaScript/Node.js
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('video', fs.createReadStream('ma_video.mp4'));

axios.post('https://ton-projet.up.railway.app/upload', form, {
    headers: form.getHeaders(),
    responseType: 'stream'
}).then(response => {
    response.data.pipe(fs.createWriteStream('video_modifiee.mp4'));
    console.log('✅ Vidéo modifiée !');
});
```

## 🔍 Endpoints disponibles

### `GET /`
Informations sur l'API

### `GET /health`
Health check

### `POST /upload`
Upload et modification d'une vidéo

**Formats acceptés** : MP4, MOV, AVI, MKV  
**Taille max** : 500 MB  
**Timeout** : 10 minutes

## 💡 Workflow recommandé

### Pour poster sur plusieurs comptes Instagram :

1. **Prépare ta vidéo originale**
2. **Modifie-la autant de fois que nécessaire** :
   ```bash
   # Pour le compte 1
   curl -X POST -F "video=@original.mp4" https://ton-api.railway.app/upload -o compte1.mp4
   
   # Pour le compte 2
   curl -X POST -F "video=@original.mp4" https://ton-api.railway.app/upload -o compte2.mp4
   
   # Pour le compte 3
   curl -X POST -F "video=@original.mp4" https://ton-api.railway.app/upload -o compte3.mp4
   ```

3. **Poste chaque version sur un compte différent**

Chaque vidéo sera **unique** pour Instagram ! 🎉

## ⚙️ Configuration

### Variables d'environnement
- `PORT` : Configuré automatiquement par Railway

### Personnalisation
Tu peux ajuster les paramètres dans `app.py` :
- Intensité du crop
- Plage de luminosité/contraste
- Probabilité de flip/rotation
- CRF (qualité)

## 🛠️ Développement local

```bash
# Installer FFmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Télécharge depuis ffmpeg.org

# Installer les dépendances Python
pip install -r requirements.txt

# Lancer le serveur
python app.py

# L'API sera sur http://localhost:5000
```

## 📊 Limites

- **Taille max** : 500 MB par fichier
- **Timeout** : 10 minutes de traitement max
- **Workers** : 2 workers Gunicorn
- **Formats** : MP4, MOV, AVI, MKV

## ⚠️ Notes importantes

- Les fichiers sont **automatiquement supprimés** après traitement
- Chaque modification est **unique** grâce à la randomisation
- Les changements sont **invisibles à l'œil nu**
- Testé et fonctionnel pour bypass la détection Instagram

## 🔒 Sécurité

- Pas d'authentification par défaut (ajoute-en si besoin)
- Fichiers temporaires auto-nettoyés
- Pas de logs persistants des uploads
- Timeout pour éviter les abus

## 🎓 Tips Instagram

Pour maximiser l'efficacité :
- Varie les hashtags entre les posts
- Poste à des heures différentes
- Utilise des légendes différentes
- Espace les publications de quelques heures/jours

## 📝 Licence

Utilise ce code comme tu veux ! 🚀

---

**Créé pour automatiser le repost de créatives sur plusieurs comptes Instagram** 💪
