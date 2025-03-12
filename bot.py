import telebot

# Bot and group details
BOT_TOKEN = "7816183726:AAG1PoexP_ttFDpqjSu5N0sWM6kwbkw7pKU"
GROUP_CHAT_ID = "-1002465666049"

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to store user data
user_data = {}

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Submit OMR", "❓ Any other query")
    bot.send_message(message.chat.id, "Welcome! Please choose an option:", reply_markup=markup)

# Handle "Submit OMR" button
@bot.message_handler(func=lambda message: message.text == "📝 Submit OMR")
def request_omr(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "Please send a photo of your OMR sheet.")

# Handle received photo
@bot.message_handler(content_types=['photo'])
def receive_omr_photo(message):
    if message.chat.id in user_data:
        user_data[message.chat.id]['photo'] = message.photo[-1].file_id
        bot.send_message(message.chat.id, "Enter the test name:")
    else:
        bot.send_message(message.chat.id, "Please start by selecting 'Submit OMR'.")

# Handle test name input
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'photo' in user_data[message.chat.id] and 'test_name' not in user_data[message.chat.id])
def receive_test_name(message):
    user_data[message.chat.id]['test_name'] = message.text
    bot.send_message(message.chat.id, "Enter your username:")

# Handle username input and submit details
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'test_name' in user_data[message.chat.id] and 'username' not in user_data[message.chat.id])
def receive_username(message):
    user_data[message.chat.id]['username'] = message.text

    # Send confirmation to user
    bot.send_message(message.chat.id, "✅ Your OMR has been submitted. The result will be sent to you soon!")

    # Forward details to group
    photo = user_data[message.chat.id]['photo']
    test_name = user_data[message.chat.id]['test_name']
    username = user_data[message.chat.id]['username']

    bot.send_photo(GROUP_CHAT_ID, photo, caption=f"📄 **New OMR Submission**\n👤 **User:** {username}\n📝 **Test Name:** {test_name}", parse_mode="Markdown")

    # Clear user data
    del user_data[message.chat.id]

# Handle "Any other query" button
@bot.message_handler(func=lambda message: message.text == "❓ Any other query")
def ask_other_query(message):
    bot.send_message(message.chat.id, "Please type your query, and we will forward it to the team.")

# Forward user queries to group
@bot.message_handler(func=lambda message: True)
def forward_query(message):
    if message.chat.id not in user_data:
        bot.send_message(GROUP_CHAT_ID, f"📩 **New Query:**\n👤 {message.from_user.username or message.from_user.first_name}\n💬 {message.text}")

# Run bot
bot.polling(none_stop=True)
