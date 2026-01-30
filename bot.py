import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import string
import subprocess
import io
from datetime import datetime, timedelta
import tempfile

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def modify_video(input_path, output_path):
    """Modifie la vidéo : métadonnées + édits légers"""
    
    # Modifications visuelles aléatoires
    modifications = []
    
    # Crop léger (1-3 pixels)
    crop_top = random.randint(0, 3)
    crop_bottom = random.randint(0, 3)
    crop_left = random.randint(0, 3)
    crop_right = random.randint(0, 3)
    modifications.append(f"crop=iw-{crop_left}-{crop_right}:ih-{crop_top}-{crop_bottom}:{crop_left}:{crop_top}")
    
    # Luminosité/contraste
    brightness = round(random.uniform(-0.02, 0.02), 3)
    contrast = round(random.uniform(0.98, 1.02), 3)
    modifications.append(f"eq=brightness={brightness}:contrast={contrast}")
    
    # Saturation
    saturation = round(random.uniform(0.98, 1.02), 3)
    modifications.append(f"eq=saturation={saturation}")
    
    # Flip horizontal (10% chance)
    if random.random() < 0.1:
        modifications.append("hflip")
    
    vf = ",".join(modifications)
    
    # Métadonnées aléatoires
    random_title = f"Video_{generate_random_string(16)}"
    random_artist = f"Creator_{generate_random_string(10)}"
    random_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    
    # Commande FFmpeg
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
        return result.returncode == 0
    except:
        return False

@bot.event
async def on_ready():
    print(f'✅ Bot connecté: {bot.user}')
    await bot.tree.sync()
    print('✅ Commandes synchronisées')

@bot.tree.command(name="modify", description="Modifie une vidéo pour éviter la détection Instagram")
async def modify(interaction: discord.Interaction, video: discord.Attachment):
    # Vérifications
    if not video.content_type or not video.content_type.startswith('video/'):
        await interaction.response.send_message("❌ Fichier invalide. Formats acceptés: MP4, MOV, AVI", ephemeral=True)
        return
    
    if video.size > 500 * 1024 * 1024:
        await interaction.response.send_message(f"❌ Fichier trop gros ({video.size/1024/1024:.1f}MB). Maximum: 500MB", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        # Télécharger la vidéo
        video_data = await video.read()
        await interaction.followup.send(f"⏳ Traitement en cours... ({video.size/1024/1024:.1f}MB)")
        
        # Créer fichiers temporaires
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as input_file:
            input_file.write(video_data)
            input_path = input_file.name
        
        output_path = input_path.replace('.mp4', '_modified.mp4')
        
        # Modifier la vidéo
        success = modify_video(input_path, output_path)
        
        if not success:
            os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
            await interaction.followup.send("❌ Erreur lors du traitement de la vidéo")
            return
        
        # Lire la vidéo modifiée
        with open(output_path, 'rb') as f:
            modified_data = f.read()
        
        # Nettoyer les fichiers temporaires
        os.remove(input_path)
        os.remove(output_path)
        
        # Envoyer la vidéo modifiée
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"modified_{timestamp}_{video.filename}"
        file = discord.File(fp=io.BytesIO(modified_data), filename=filename)
        
        await interaction.followup.send(
            f"✅ Vidéo modifiée avec succès!\n"
            f"📦 Taille originale: {video.size/1024/1024:.1f}MB\n"
            f"📦 Taille modifiée: {len(modified_data)/1024/1024:.1f}MB\n"
            f"🎨 Modifications: métadonnées + édits visuels légers",
            file=file
        )
        
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur: {str(e)}")

@bot.tree.command(name="help", description="Affiche l'aide")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎥 Video Modifier Bot",
        description="Modifie les vidéos pour éviter la détection Instagram",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📝 Commande",
        value="`/modify [vidéo]` - Modifie une vidéo",
        inline=False
    )
    embed.add_field(
        name="🎨 Modifications appliquées",
        value=(
            "✅ Métadonnées aléatoires (titre, artiste, date)\n"
            "✅ Crop imperceptible (1-3 pixels)\n"
            "✅ Luminosité/contraste (-2% à +2%)\n"
            "✅ Saturation (98% à 102%)\n"
            "✅ Flip horizontal (10% chance)"
        ),
        inline=False
    )
    embed.add_field(name="📋 Formats", value="MP4, MOV, AVI", inline=True)
    embed.add_field(name="📦 Taille max", value="500MB", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.command(name='modify')
async def modify_classic(ctx):
    """Commande classique avec ! """
    if not ctx.message.attachments:
        await ctx.send("❌ Attache une vidéo à ton message!\nUsage: `!modify` + vidéo")
        return
    
    attachment = ctx.message.attachments[0]
    
    if not attachment.content_type or not attachment.content_type.startswith('video/'):
        await ctx.send("❌ Fichier invalide. Formats: MP4, MOV, AVI")
        return
    
    if attachment.size > 500 * 1024 * 1024:
        await ctx.send(f"❌ Trop gros ({attachment.size/1024/1024:.1f}MB). Max: 500MB")
        return
    
    msg = await ctx.send(f"⏳ Traitement... ({attachment.size/1024/1024:.1f}MB)")
    
    try:
        video_data = await attachment.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as input_file:
            input_file.write(video_data)
            input_path = input_file.name
        
        output_path = input_path.replace('.mp4', '_modified.mp4')
        
        success = modify_video(input_path, output_path)
        
        if not success:
            os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
            await msg.edit(content="❌ Erreur lors du traitement")
            return
        
        with open(output_path, 'rb') as f:
            modified_data = f.read()
        
        os.remove(input_path)
        os.remove(output_path)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"modified_{timestamp}_{attachment.filename}"
        file = discord.File(fp=io.BytesIO(modified_data), filename=filename)
        
        await msg.edit(content=f"✅ Done! ({len(modified_data)/1024/1024:.1f}MB)")
        await ctx.send(file=file)
        
    except Exception as e:
        await msg.edit(content=f"❌ Erreur: {str(e)}")

if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN manquant!")
        exit(1)
    bot.run(DISCORD_TOKEN)
