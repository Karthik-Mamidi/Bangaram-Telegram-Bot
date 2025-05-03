import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import time
import threading
import os

# === CONFIG from Environment Variables ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
HF_MODEL = 'mistralai/Mistral-7B-Instruct-v0.1'  # You can change model if needed

# === LOGGING ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# === Hugging Face Request ===
def get_ai_reply(user_message):
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
    json_data = {
        "inputs": f"You are Bangaram, a caring AI sister. Reply emotionally like a real chelli to this message: '{user_message}'"
    }
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=json_data
    )
    if response.status_code == 200:
        return response.json()[0]['generated_text'].split(":")[-1].strip()
    else:
        return "Sorry annaya, Bangaram ki problem ayyindhi… inka try chesthanu!"

# === Message Handler ===
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    ai_response = get_ai_reply(user_msg)
    await update.message.reply_text(ai_response)

# === Function to Start the Bot ===
def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))
    logging.info("Bangaram bot is running...")
    app.run_polling()

# === Run the Bot in Background Thread ===
def run_bot_thread():
    thread = threading.Thread(target=start_bot)
    thread.start()

# === Entry Point ===
if __name__ == "__main__":
    run_bot_thread()
    while True:
        time.sleep(60)  # Keeps the container running
