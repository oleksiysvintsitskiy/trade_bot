import config
import telebot
import sys
import random

bot = telebot.TeleBot(config.token)
bot.send_message(365111013, "Invalid python library name")

sys.exit()

def repeat_all_messages(message):
	print(message)
	bot.send_message(chaId, message.text)
