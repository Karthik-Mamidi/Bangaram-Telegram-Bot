import requests
import telebot
from indic_transliteration import sanscript

# Tokens and constants
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
HUGGINGFACE_API_TOKEN = 'YOUR_HUGGINGFACE_API_TOKEN'
DEFAULT_MODEL_NAME = "ai4bharat/IndicBART-Telugu"
MAX_RESPONSE_LENGTH = 4096

class TeluguBot(telebot.TeleBot):
    def __init__(self, token=TELEGRAM_BOT_TOKEN):
        super().__init__(token)
        self.huggingface_api_token = HUGGINGFACE_API_TOKEN
        self.model_name = DEFAULT_MODEL_NAME
        self.transliteration_model = sanscript.ITRANS

    def query_huggingface(self, text):
        headers = {"Authorization": f"Bearer {self.huggingface_api_token}"}
        payload = {"inputs": text}
        response = requests.post(
            "https://api-inference.huggingface.co/models/{}".format(self.model_name),
            headers=headers,
            json=payload
        )
        try:
            result = response.json()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return {"error": "Failed to parse response"}

    def transliterate_text(self, text):
        return self.transliteration_model.transliterate(text)

    async def handle_message(self, message):
        user_text = message.text
        await self.send_chat_action(message.chat.id, 'typing')

        # Convert English text to Telugu script and make API call
        telugu_response = self.query_huggingface(self.translitigate_text(user_text))

        if isinstance(telugu_response.get("label"), str) or "error" in telugu_response:
            reply = f"Label: {telugu_response['label']}\nConfidence: 0%"
        elif "generated_text" in telugu_response:
            reply = telugu_response["generated_text"]
        else:
            # Add default values for missing fields
            label = "Unknown"
            score = 0.0

        # Convert model's response to English letters and send it back
        english_reply = self.translitigate_text(reply)
        await self.send_message(message.chat.id, english_reply)

    async def handle_command(self, message):
        if message.command == '/start':
            await self.send_start_message(message)
        elif message.command.startswith('/help'):
            await self.send_help_message(message)

async def send_start_message(message):
    # Send a welcome message with instructions
    await bot.send_text(message.chat.id, "Welcome to the Telugu Bot!")

async def send_help_message(message):
    # Send help text with available commands
    await bot.send_text(message.chat.id, "/start - Start the conversation\n/help - Show this help message")

def main():
    global bot
    bot = TeluguBot()
    bot.set_update_listener(bot.on_update)
    print("Bot is running...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()
