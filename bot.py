import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
import io
from datetime import datetime

# Config
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = os.getenv('API_URL')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} connecté')
    print(f'📡 API: {API_URL}')
    await bot.tree.sync()
    print(f'✅ Commandes synchronisées')

@bot.tree.command(name="modify", description="Modifie une vidéo pour éviter la détection Instagram")
async def modify(interaction: discord.Interaction, video: discord.Attachment):
    if not video.content_type or not video.content_type.startswith('video/'):
        await interaction.response.send_message("❌ Fichier invalide (MP4/MOV/AVI uniquement)", ephemeral=True)
        return
    
    if video.size > 500 * 1024 * 1024:
        await interaction.response.send_message(f"❌ Trop gros ({video.size/1024/1024:.1f}MB). Max: 500MB", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        video_data = await video.read()
        await interaction.followup.send(f"⏳ Traitement... ({video.size/1024/1024:.1f}MB)")
        
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field('video', video_data, filename=video.filename, content_type=video.content_type)
            
            async with session.post(f'{API_URL}/upload', data=form, timeout=aiohttp.ClientTimeout(total=600)) as response:
                if response.status == 200:
                    modified = await response.read()
                    file = discord.File(fp=io.BytesIO(modified), filename=f"modified_{video.filename}")
                    await interaction.followup.send(f"✅ Done! ({len(modified)/1024/1024:.1f}MB)", file=file)
                else:
                    await interaction.followup.send(f"❌ Erreur: {await response.text()}")
    except Exception as e:
        await interaction.followup.send(f"❌ {str(e)}")

@bot.tree.command(name="status", description="Statut de l'API")
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{API_URL}/health', timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    await interaction.followup.send(f"✅ API OK\n```{await r.text()}```")
                else:
                    await interaction.followup.send(f"⚠️ Code {r.status}")
    except:
        await interaction.followup.send("❌ API offline")

bot.run(DISCORD_TOKEN)
