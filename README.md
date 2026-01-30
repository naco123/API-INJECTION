# 🎥 Discord Video Modifier Bot

Bot Discord qui modifie les vidéos directement pour éviter la détection Instagram.

## ✨ Fonctionnalités

Le bot modifie automatiquement :
- ✅ Métadonnées (titre, artiste, date, commentaire)
- ✅ Crop imperceptible (1-3 pixels)
- ✅ Luminosité/contraste (-2% à +2%)
- ✅ Saturation (98% à 102%)
- ✅ Flip horizontal aléatoire (10% chance)

## 🚀 Déploiement sur Railway

### 1. Créer le bot Discord

1. Va sur https://discord.com/developers/applications
2. **New Application** → Nom du bot
3. **Bot** → **Add Bot** → **Copie le TOKEN**
4. Active **MESSAGE CONTENT INTENT**
5. **OAuth2** → **URL Generator** :
   - Scopes: `bot` + `applications.commands`
   - Permissions: `Send Messages`, `Attach Files`, `Use Slash Commands`
6. Copie l'URL et invite le bot sur ton serveur

### 2. Déployer sur Railway

1. Push ce repo sur GitHub
2. Railway → **New Project** → **Deploy from GitHub**
3. Sélectionne ton repo
4. Dans **Variables**, ajoute :
   ```
   DISCORD_TOKEN = ton_token_ici
   ```
5. Deploy automatique ✅

## 🎮 Utilisation

Dans Discord :
- `/modify [vidéo]` - Modifie une vidéo
- `/help` - Affiche l'aide
- `!modify` + attacher vidéo - Alternative

## 📋 Limites

- **Formats** : MP4, MOV, AVI
- **Taille max** : 500MB
- **Timeout** : 5 minutes

## 🛠️ Structure

```
bot.py              # Le bot Discord avec FFmpeg intégré
requirements.txt    # discord.py
nixpacks.toml      # Config Railway (Python + FFmpeg)
.gitignore         # Sécurité
```

## 🔐 Sécurité

⚠️ **NE JAMAIS commit ton `DISCORD_TOKEN`**
✅ Utilise toujours les variables d'environnement Railway

---

Fait avec ❤️ pour contourner la détection Instagram
