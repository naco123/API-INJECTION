# Discord Video Modifier Bot

Bot Discord qui modifie les vidéos pour éviter la détection Instagram.

## 🚀 Déploiement Railway

1. **Push sur GitHub**
2. **Railway** → New Project → Deploy from GitHub
3. **Variables d'environnement** (dans Railway) :
   - `DISCORD_TOKEN` = ton_token_discord
   - `API_URL` = https://ton-api.up.railway.app
4. Deploy automatique ✅

## 🎮 Commandes Discord

- `/modify [vidéo]` - Modifie une vidéo
- `/status` - Statut de l'API

## 📋 Setup Discord Bot

1. https://discord.com/developers/applications
2. New Application → Bot → Copy Token
3. OAuth2 → URL Generator :
   - Scopes: `bot` + `applications.commands`
   - Permissions: `Send Messages`, `Attach Files`
4. Invite le bot sur ton serveur

---

**Formats**: MP4, MOV, AVI | **Max**: 500MB
