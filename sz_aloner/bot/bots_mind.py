import os
import re
import time
import pickle
import config
import requests
import telebot
from telebot import types
import re
import json
import steamchat
from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions

client = 0
with open('ram.json', 'r') as f:
	chats = json.load(f)

bot = telebot.TeleBot(config.token)

for chat in chats:
	#bot.send_message(chat, 'Ебать, чё вчера было-то?')
	if chats[chat]["act"] == "waiting for nickname":
		bot.send_message(chat, 'Ти там вродь мені мав свій нікнейм написать, вроде')
	if chats[chat]["act"] == "waiting for sum":
		bot.send_message(chat, 'Давай там по фасту пиши скільки вивести хочеш')
	elif chats[chat]["act"] == "waiting for getmoney accept":
		chats[chat]["act"] = "waiting for sum"
		bot.send_message(chat, 'Ти там вроді мав законфірмить лавеху, але шось по пізді пішло, так шо давай пиши заново скільки лавехи хочеш')
	elif chats[chat]["act"] == "waiting for logfile name":
		logs_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
		logs_markup.add(types.KeyboardButton('siziph'), types.KeyboardButton('predivider'), types.KeyboardButton('divider'), types.KeyboardButton('keys_exchanger'), types.KeyboardButton('user1'), types.KeyboardButton('user2'))
		bot.send_message(chat, "Вибирай лог уже:", reply_markup=logs_markup)
	else:
		reg_test = re.search('waiting for (user[12]) logfile', chats[chat]["act"])
		if reg_test:
			#user = reg_test.group(1)
			logs_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
			logs_markup.add(types.KeyboardButton('separator'), types.KeyboardButton('withdraw'), types.KeyboardButton('empauto'))
			bot.send_message(chat, "Вибирай лог уже:", reply_markup=logs_markup)

@bot.message_handler(content_types=["text"])
def commands_messages(message):
	chat = str(message.chat.id)
	if not chat in chats:
		chats[chat] = {"act": ""}
	if message.text == '/set_user':
		chats[chat]["act"] = "waiting for nickname"
		bot.send_message(message.chat.id, 'Ну давай, спіздани чот')
	elif message.text == '/get_money':
		chats[chat]["act"] = "waiting for sum"
		bot.send_message(message.chat.id, 'Скільки нада?')
	elif message.text == '/get_log':
		chats[chat]["act"] = "waiting for logfile name"
		logs_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
		logs_markup.add(types.KeyboardButton('siziph'), types.KeyboardButton('predivider'), types.KeyboardButton('divider'), types.KeyboardButton('keys_exchanger'), types.KeyboardButton('user1'), types.KeyboardButton('user2'))
		bot.send_message(message.chat.id, "Вибирай лог:", reply_markup=logs_markup)
	else:
		if chats[chat]["act"] == "waiting for nickname":
			matches = re.search(r'^[a-zA-Z0-9][a-zA-Z\-_0-9]*[a-zA-Z0-9]$', message.text)
			if matches == None:
				bot.send_message(message.chat.id, 'Нік може містить тільки латинські букви, цифри і знаки "-", "_", аутист')
			else:
				with open('users.json', 'r') as f:
					users = json.load(f)

				for name in users:
					if users[name] == message.chat.id:
						del users[name]
						break
				users[message.text] = message.chat.id

				with open('users.json', 'w', encoding="utf8") as f:
					json.dump(users, f)
				chats[chat]["act"] = ""
				bot.send_message(message.chat.id, 'Харош')
		elif chats[chat]["act"] == "waiting for sum":
			preg_res = re.search(r"^[0-9]+(\.[0-9]{1,2})?$", message.text)
			if preg_res:
				bot.send_message(message.chat.id, 'Парсек')
				price = float(preg_res.group())
				
				USER = ""

				if message.chat.id == 96580305:
					USER = "user1"
				elif message.chat.id == 365111522:
					USER = "user2"

				if USER == "":
					bot.send_message(message.chat.id, 'Бля, іди нахуй, я тебе не знаю.')
					chats[chat]["act"] = ""
				else:
					with open('../'+USER+'.pickle', 'rb') as f:
						client = pickle.load(f)

					with open('../cookies.json', 'r') as f:
						all_cookies = json.load(f)

					if not client.is_session_alive():
						client = SteamClient(all_cookies[USER]['api'])
						attemts = 0
						while (1):
							if attemts == 3:
								bot.send_message(message.chat.id, 'Там походу роутер над перезагрузить, я єбу.')
								chats[chat]["act"] = ""
								break
							try:
								client.login(all_cookies[USER]['username'], all_cookies[USER]['password'], all_cookies[USER]['sgpath'])
							except Exception as e:
								attemts += 1
								print(e)
								time.sleep(10)
								continue
							else:
								break
						with open('../'+USER+'.pickle', 'wb') as f:
							pickle.dump(client, f)

					cookies = {'Cookie':'__cfduid='+all_cookies[USER]['cm']['__cfduid']+';steamid='+all_cookies[USER]['steamid']+';new_1_csrf='+all_cookies[USER]['cm']['csrf']}
					hdrs = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br',
											  'accept-language': 'en-US,en;q=0.8,ru;q=0.6,uk;q=0.4',
											  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
											  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
											  'x-requested-with': 'XMLHttpRequest'}

					while(1):
						try:
							sp1 = requests.get('https://cs.money/load_inventory?hash='+str(int(time.time()*1000)), headers=hdrs, cookies=cookies)
							mark1 = sp1.content
							prices1 = mark1.decode("utf-8")
							prs1 = json.loads(prices1)
							keys = []
							keys_id = []
							for i in prs1:
								if i['t'] == 'ky':
									keys.append(i['p'])
									keys_id.append(i['id'])
							break
						except Exception as e:
							print(e)
							time.sleep(3)

					if len(keys) == 0:
						bot.send_message(message.chat.id, 'У тебе ключів ніхуя нема, ніщеброд єбаний)))')
						chats[chat]["act"] = ""
					else:
						n = len(keys)
						W = int(price*100)
						for i in range(len(keys)):
							keys[i] = int(keys[i]*100)
						K = [[0 for x in range(W+1)] for x in range(n+1)]
						for i in range(n+1):
							for w in range(W+1):
								if i==0 or w==0:
									K[i][w] = 0
								elif keys[i-1] <= w:
									K[i][w] = max(keys[i-1] + K[i-1][w-keys[i-1]],  K[i-1][w])
								else:
									K[i][w] = K[i-1][w]
					
						res_deal = []
						def findans(i, j):
							if K[i][j] == 0:
								return
							if K[i-1][j] == K[i][j]:
								findans(i-1, j)
							else:
								findans(i-1, j-keys[i-1])
								res_deal.append(keys_id[i-1])

						findans(n, W)
						with open('keys.json', 'r') as f:
							keys_dump = json.load(f)

						keys_dump[str(message.chat.id)] = res_deal

						with open('keys.json', 'w', encoding="utf8") as f:
							json.dump(keys_dump, f)

						if K[n][W]/100. == price:
							keys_dump[str(message.chat.id)] = []

							with open('keys.json', 'w', encoding="utf8") as f:
								json.dump(keys_dump, f)
							bot.send_message(message.chat.id, 'Чотка, якраз стільки і є. Жди')
							bot.send_message(message.chat.id, 'У тебе там в сумі {}$, якщо що.'.format(round(sum(keys)/100, 2)))

							trade1 = []
							game = GameOptions.CS 
							for key_id in res_deal:
								trade1.append(Asset(key_id,game))

							try:
								client.make_offer(trade1, [], 76561198219924665)
							except:
								bot.send_message(message.chat.id, 'Там якась помилка з офером, попробуй повторить')
								chats[chat]["act"] = ""
								return

							bot.send_message(message.chat.id, 'Офер відіслав, ждем')
							
							hrn_result = 0
							
							while True:
								msg = steamchat.get_last_message(client, 259658937)
								if time.time() - msg['time'] < 600: # 5min
									preg_res = re.search("(К выплате:  )(.*)( грн)", msg['text'])
									if preg_res:
										hrn_result = preg_res.group(2)
										break
								time.sleep(5)

							steamchat.send_message(USER, client, "!accept", 76561198219924665)
							bot.send_message(message.chat.id, 'Все ок, получиш {} гривин'.format(hrn_result))
							chats[chat]["act"] = ""
						else:
							bot.send_message(message.chat.id, 'Ну там в сумі в тебе {}$, тільки {}$ вийде. Нормас?'.format(round(sum(keys)/100, 2), round(K[n][W]/100, 2)))
							chats[chat]["act"] = "waiting for getmoney accept"
			else:
				bot.send_message(message.chat.id, 'Собери єбало і напиши нормально, яка це нахуй цена для виводу?')
		elif chats[chat]["act"] == "waiting for getmoney accept":
			ans = message.text.lower()
			if ans in ["да", "yes", "так", "da", "збс", "ну да", "угу", "ага"]:
				bot.send_message(message.chat.id, 'Падажжи ебана')
				with open('keys.json', 'r') as f:
					keys_dump = json.load(f)

				res_deal = keys_dump[str(message.chat.id)]
				
				keys_dump[str(message.chat.id)] = []
				
				with open('keys.json', 'w', encoding="utf8") as f:
					json.dump(keys_dump, f)

				if message.chat.id == 96580305:
					USER = "user1"
				elif message.chat.id == 365111522:
					USER = "user2"

				with open('../'+USER+'.pickle', 'rb') as f:
					client = pickle.load(f)

				if not client.is_session_alive():
					client = SteamClient(all_cookies[USER]['api'])
					attemts = 0
					while (1):
						if attemts == 3:
							bot.send_message(message.chat.id, 'Там походу роутер над перезагрузить, я єбу.')
							chats[chat]["act"] = ""
							break
						try:
							client.login(all_cookies[USER]['username'], all_cookies[USER]['password'], all_cookies[USER]['sgpath'])
						except Exception as e:
							attemts += 1
							print(e)
							time.sleep(10)
							continue
						else:
							break
					with open('../'+USER+'.pickle', 'wb') as f:
						pickle.dump(client, f)

				trade1 = []
				game = GameOptions.CS 
				for key_id in res_deal:
					trade1.append(Asset(key_id,game))

				client.make_offer(trade1, [], 76561198219924665)

				bot.send_message(message.chat.id, 'Офер відіслав, ждем')

				hrn_result = 0
				
				while True:
					msg = steamchat.get_last_message(client, 259658937)
					if time.time() - msg['time'] < 600: # 5min
						preg_res = re.search("(К выплате:  )(.*)( грн)", msg['text'])
						if preg_res:
							hrn_result = preg_res.group(2)
							break
					time.sleep(5)

				steamchat.send_message(USER, client, "!accept", 76561198219924665)
				bot.send_message(message.chat.id, 'Все ок, получиш {} гривин'.format(hrn_result))
				chats[chat]["act"] = ""
			elif ans in ["ні", "нє", "ni", "no", "ne", "ніхуя", "нихуя", "otmena", "отмена", "відміна"]:
				chats[chat]["act"] = ""
				bot.send_message(message.chat.id, 'Ебать ти баклажан, хуею з тебе')
			else:
				bot.send_message(message.chat.id, 'Ніхуя не поняв')
		elif chats[chat]["act"] == "waiting for logfile name":
			filename = ''
			chats[chat]["act"] = ""
			if message.text == 'divider' or message.text == 'predivider' or message.text == 'keys_exchanger':
				filename = message.text
				path = "../logs/bot"
				files = os.listdir(path)
				files = [os.path.join(path, file) for file in files]
				files = [file for file in files if (os.path.isfile(file) and (file.find("\\"+filename) != -1 or file.find("/"+filename) != -1))]
				bot.send_document(message.chat.id, open(max(files, key=os.path.getctime), 'r'), reply_markup=telebot.types.ReplyKeyboardRemove())
			elif message.text == 'siziph':
				bot.send_document(message.chat.id, open('../logs/siziph_final.log', 'r'), reply_markup=telebot.types.ReplyKeyboardRemove())
			elif message.text == 'user1' or message.text == 'user2':
				logs_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
				logs_markup.add(types.KeyboardButton('separator'), types.KeyboardButton('withdraw'), types.KeyboardButton('empauto'))
				bot.send_message(chat, "Чо саме:", reply_markup=logs_markup)
				chats[chat]["act"] = "waiting for "+message.text+" logfile"
			else:
				bot.send_message(chat, 'Блять, я попросив на кнопку одну нажать, ну шо ти за овощ, їй-богу', reply_markup=telebot.types.ReplyKeyboardRemove())
		elif chats[chat]["act"] == "waiting for user1 logfile" or chats[chat]["act"] == "waiting for user2 logfile":
			reg_test = re.search('^(withdraw|separator|empauto)$', message.text)
			if reg_test:
				user = "user1" if chats[chat]["act"].find("user1") != -1 else "user2"
				filename = reg_test.group(1)
				path = "../logs/bot/"+user
				files = os.listdir(path)
				files = [os.path.join(path, file) for file in files]
				files = [file for file in files if (os.path.isfile(file) and (file.find("\\"+filename) != -1 or file.find("/"+filename) != -1))]
				bot.send_document(message.chat.id, open(max(files, key=os.path.getctime), 'r'), reply_markup=telebot.types.ReplyKeyboardRemove())
			else:
				bot.send_message(chat, 'Блять, я попросив на кнопку одну нажать, ну шо ти за овощ, їй-богу', reply_markup=telebot.types.ReplyKeyboardRemove())
			chats[chat]["act"] = ""
		else:
			bot.send_message(message.chat.id, 'І шо я маю робить з цією інформацією?')
	with open('ram.json', 'w', encoding="utf8") as f:
		json.dump(chats, f)

if __name__ == '__main__':
	bot.polling(none_stop=True)