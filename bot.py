import requests
import telebot
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Tokens
telegram_token = 'YOUR_TELEGRAM_BOT_TOKEN'  # Replace with your Telegram bot token
hf_token = 'YOUR_HUGGINGFACE_API_TOKEN'     # Replace with your Hugging Face API token
model_id = 'ai4bharat/IndicBART-Telugu'     # You can change this to any Telugu model

# Initialize bot
bot = telebot.TeleBot(telegram_token)

# Hugging Face API Function
def query_huggingface(text):
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": text}
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{model_id}",
        headers=headers,
        json=payload
    )
    try:
        result = response.json()
        return result
    except:
        return {"error": "Failed to parse response"}

# Transliteration function: English to Telugu and back
def transliterate_text(text):
    # Convert English letters to Telugu script
    text_telugu = transliterate(text, sanscript.ITRANS, sanscript.TELUGU)
    return text_telugu

# Handle incoming messages
@bot.message_handler(func=lambda message: True)
def respond(message):
    user_text = message.text
    bot.send_chat_action(message.chat.id, 'typing')

    # Convert English text to Telugu script
    user_text_telugu = transliterate_text(user_text)
    
    hf_response = query_huggingface(user_text_telugu)

    # Response parsing (based on model type)
    if isinstance(hf_response, list):
        label = hf_response[0].get('label', 'Unknown')
        score = hf_response[0].get('score', 0)
        reply = f"Label: {label}\nConfidence: {round(score * 100, 2)}%"
    elif "generated_text" in hf_response:
        reply = hf_response["generated_text"]
    elif "error" in hf_response:
        reply = f"Error: {hf_response['error']}"
    else:
        reply = str(hf_response)

    # Convert the model's response to English letters
    reply_in_english = transliterate(reply, sanscript.TELUGU, sanscript.ITRANS)
    bot.reply_to(message, reply_in_english)

# Start polling
print("Bot is running...")
bot.infinity_polling()
