import config
import telebot
import sys
import random

bot = telebot.TeleBot(config.token)
bot.send_message(365111522, "Invalid python library name, dolboeb")

sys.exit()
#bot.send_message(96580305, "Один. Один. Проверка. Хуй саси губой тряси")
def repeat_all_messages(message):
	print(message)
	bot.send_message(chaId, message.text)

# if __name__ == '__main__':
#     #bot.polling(none_stop=True)
#     bot.polling()