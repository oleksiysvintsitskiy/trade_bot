import telebot
from bot import config
from json import load

with open('bot/users.json', 'r') as f:
	users = load(f)
def write(message, *args):
	for username in args:
		if username in users:
			bot = telebot.TeleBot(config.token)
			bot.send_message(users[username], message)
			#print(message)

def send_voice(filepath, username):
	if username in users:
		bot = telebot.TeleBot(config.token)
		bot.send_voice(users[username], open(filepath, 'rb'))

def send_photo(filepath, username):
	if username in users:
		bot = telebot.TeleBot(config.token)
		bot.send_photo(users[username], open(filepath, 'rb'))