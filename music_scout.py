#!/usr/bin/env python3
import os, asyncio, logging, subprocess, tempfile
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8981207314:AAF_vkG8MOkX1_kd94FreajYW_zNL_-4zps"
CHAT_ID = "8320513131"
DOWNLOAD_DIR = Path("/tmp/music_scout")
DOWNLOAD_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO)

async def run_yt_dlp(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            mp3_files = sorted(DOWNLOAD_DIR.glob("*.mp3"), key=os.path.getmtime, reverse=True)
            if mp3_files:
                return True, str(mp3_files[0])
    except Exception as e:
        print(f"Pipeline error: {e}")
    return False, ""

async def youtube_pipeline(query):
    return await run_yt_dlp(["yt-dlp", f"ytsearch1:{query}", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0", "--output", str(DOWNLOAD_DIR / "%(title)s.%(ext)s"), "--no-playlist", "--quiet"])

async def soundcloud_pipeline(query):
    return await run_yt_dlp(["yt-dlp", f"scsearch1:{query}", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0", "--output", str(DOWNLOAD_DIR / "scouted_track.%(ext)s"), "--no-playlist", "--quiet"])

async def audiomack_pipeline(query):
    return await run_yt_dlp(["yt-dlp", f"https://audiomack.com/search?q={query.replace(' ', '+')}", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0", "--output", str(DOWNLOAD_DIR / "audiomack_track.%(ext)s"), "--no-playlist", "--quiet", "--playlist-items", "1"])

async def youtube_music_pipeline(query):
    return await run_yt_dlp(["yt-dlp", f"https://music.youtube.com/search?q={query.replace(' ', '+')}", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0", "--output", str(DOWNLOAD_DIR / "ytmusic_track.%(ext)s"), "--no-playlist", "--quiet", "--playlist-items", "1"])

async def download_and_send(query, update, context):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=f"👑 KINGALMOND MUSIC SCOUT\n\n🎵 Searching: {query}\n🔄 Engaging pipelines...")

    pipelines = [
        ("YOUTUBE", youtube_pipeline),
        ("YOUTUBE MUSIC", youtube_music_pipeline),
        ("SOUNDCLOUD", soundcloud_pipeline),
        ("AUDIOMACK", audiomack_pipeline),
    ]

    success, filepath, pipeline_used = False, "", ""
    for name, pipeline in pipelines:
        await context.bot.send_message(chat_id=chat_id, text=f"🔍 Trying {name}...")
        success, filepath = await pipeline(query)
        if success:
            pipeline_used = name
            break

    if success and filepath and os.path.exists(filepath):
        await context.bot.send_message(chat_id=chat_id, text=f"👑 KINGALMOND MUSIC SCOUT\n\n🎵 Track: {query}\n🎯 Status: ACQUIRED VIA {pipeline_used} PIPELINE")
        with open(filepath, "rb") as f:
            await context.bot.send_audio(chat_id=chat_id, audio=f, title=query, performer="KINGALMOND SCOUT")
        try:
            os.remove(filepath)
        except:
            pass
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Could not find: {query}\nTry adding artist name + song title")

async def start(update, context):
    await update.message.reply_text("👑 KINGALMOND MUSIC SCOUT\n\n4 Pipelines Active:\n✅ YouTube\n✅ YouTube Music\n✅ SoundCloud\n✅ Audiomack\n\nJust type any song name!")

async def handle_message(update, context):
    await download_and_send(update.message.text.strip(), update, context)

def main():
    print("👑 KINGALMOND MUSIC SCOUT STARTING...")
    print("✅ Pipelines: YouTube | YouTube Music | SoundCloud | Audiomack")
    app = ApplicationBuilder().token(TOKEN).read_timeout(60).write_timeout(60).connect_timeout(60).pool_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is live!")
    app.run_polling()

if __name__ == "__main__":
    main()
