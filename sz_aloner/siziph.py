from subprocess import Popen
import re
import os
import sys
from multiprocessing import Process
import json
import time
import hustle
import logging
from hacks import log as print
import requests
import cfscrape

# def open_and_Wait(arg):
# 	proc = Popen(arg)
#     proc.wait()
SYS_EXECUTABLE = sys.executable
NODE_EXECUTABLE = "node"

def start_rolling(sum1, sum2):
	if sum1 > 0 and sum2 > 0:
		with open('logs/withdraw.json', 'w', encoding="utf8") as f:
			json.dump({"user1": sum1, "user2": sum2}, f)
		roll_bot = Popen([NODE_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\nodejs\\roulette_bot.js'])
		roll_bot.wait()
		withdraw_obj = {}
		while True:
			while True:
				try:
					with open('logs/withdraw.json', 'r') as f:
						withdraw_obj = json.load(f)
					break
				except BaseException as e:
					print(e)
			if withdraw_obj['user1'] == 0 and withdraw_obj['user2'] == 0:
				if 'rolled' in withdraw_obj:
					if withdraw_obj['rolled'] == True:
						del withdraw_obj['rolled']
						with open('logs/withdraw.json', 'w') as f:
							json.dump(withdraw_obj, f)
						del withdraw_obj
						break
		time.sleep(20)
		print("Starting withdraw")
		hustle.write("Починаю виводить", "house_trader")
		return "ok"

def getBalanceInfo():
	with open('cookies.json', 'r') as f:
		all_cookies = json.load(f)

	hdrs = {'User-Agent': 'Mozilla / 537.36 (KHTML, like Gecko) Chrome /'}

	balanceInfo = []
	keys_num = {"user1": 0, "user2": 0}
	keys_sum = {"user1": 0, "user2": 0}

	for USER in all_cookies:
		scraper = cfscrape.create_scraper()
		r = scraper.get('https://csgoempire.com/deposit', headers=hdrs, cookies={'__cfduid': all_cookies[USER]['emp']['__cfduid'], 'PHPSESSID': all_cookies[USER]['emp']['PHPSESSID']})
		page = r.content.decode("utf-8")
		start = page.find('<animated-integer v-bind:value="balance" id="balance">') + 54
		end = page.find('</animated-integer>')
		balanceInfo.append(float(r.content.decode("utf-8")[start:end]))
		
		cookies = {'Cookie':'__cfduid='+all_cookies[USER]['cm']['__cfduid']+';steamid='+all_cookies[USER]['steamid']+';new_1_csrf='+all_cookies[USER]['cm']['csrf']}
		hdrs = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br',
								  'accept-language': 'en-US,en;q=0.8,ru;q=0.6,uk;q=0.4',
								  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
								  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
								  'x-requested-with': 'XMLHttpRequest'}
		while(1):
			try:
				scraper = cfscrape.create_scraper()
				sp1 = scraper.get('https://cs.money/load_inventory?hash='+str(int(time.time()*1000)), headers=hdrs, cookies=cookies)
				mark1 = sp1.content
				prices1 = mark1.decode("utf-8")
				prs1 = json.loads(prices1)
				sum1 = 0
				for i in prs1:
					sum1 += i['p']*(i['r']+2)/100.
					if i['t'] == 'ky':
						keys_num[USER] += 1
						keys_sum[USER] += i['p']*(i['r']+2)/100.
				break
			except Exception as e:
				print(e)
				time.sleep(3)
		sum1 = round(sum1,2)
		keys_sum[USER] = round(keys_sum[USER], 2)
		balanceInfo.append(round(sum1, 2))

	balanceInfo.extend([round(balanceInfo[0] + balanceInfo[1] + balanceInfo[2] + balanceInfo[3], 2), keys_num, keys_sum])
	return balanceInfo

def get_withdraw_info(user, user_cookies):
	cookies = {'__cfduid': user_cookies['emp']['__cfduid'], 'PHPSESSID': user_cookies['emp']['PHPSESSID']}
	trade_url = user_cookies['emp']['trade_url']

	headers = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br',
					  'accept-language': 'en-US,en;q=0.8,ru;q=0.6,uk;q=0.4',
					  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
					  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
					  'x-requested-with': 'XMLHttpRequest'}

	s = requests.Session()
	s.cookies.update(cookies)
	counter = 0
	while(True):
		if counter>=3:
			return 0
		setOffer = s.post('https://csgoempire.com/api/set_trade_url', data={"trade_url": trade_url}, headers=headers)

		data = "transfer_type=withdraw&item_ids%5B%5D="
		r = s.post('https://csgoempire.com/api/transfer_items', data = data, headers = headers)
		balance_reg = re.search("<strong>([0-9]+(\.[0-9]+)?)<", r.text)
		if balance_reg:
			return float(balance_reg.group(1))
		else:
			counter += 1

if __name__ == "__main__":
	logging.basicConfig(format='%(asctime)s | %(message)s', datefmt='%d.%m.%Y %H:%M:%S', filemode='a', filename="logs/siziph_final.log")
	print('\n\n--------------------------------------  '+time.strftime("%d.%m.%Y %H:%M:%S")+'  --------------------------------------\n')
	while True:
		task = open("tasks.json", "r+", encoding='utf8')
		cur_task = json.load(task)

		if cur_task['predivider'] == False and cur_task['withdraw']['user1']==False and cur_task['withdraw']['user2']==False and not "start_bankroll" in cur_task:
			startBalance = getBalanceInfo()
			key_ukr1 = "ключів" if startBalance[5]['user1'] in range(5, 21) or startBalance[5]['user1']%100 in range(5, 21) else ("ключ" if startBalance[5]['user1']%10 == 1 else ("ключа" if startBalance[5]['user1']%10 == 2 else ("ключі" if startBalance[5]['user1']%10 in [3,4] else "ключів")))
			key_ukr2 = "ключів" if startBalance[5]['user2'] in range(5, 21) or startBalance[5]['user2']%100 in range(5, 21) else ("ключ" if startBalance[5]['user2']%10 == 1 else ("ключа" if startBalance[5]['user2']%10 == 2 else ("ключі" if startBalance[5]['user2']%10 in [3,4] else "ключів")))
			startBalanceInfo = "Загальний банк - {}$\nStaison починає з {}$ ({}$ на cs.money + {} {} на {}$ і {}$ на empire)\nLeha почав з {}$ ({}$ на cs.money + {} {} сумарно на {}$ і {}$ на empire)\n".format(startBalance[4], round(startBalance[0]+startBalance[1], 2), round(startBalance[1]-startBalance[6]['user1'], 2), startBalance[5]['user1'], key_ukr1, startBalance[6]['user1'], startBalance[0], round(startBalance[3]+startBalance[2], 2), round(startBalance[3]-startBalance[6]['user2'], 2), startBalance[5]['user2'], key_ukr2, startBalance[6]['user2'], startBalance[2])
			cur_task['start_bankroll'] = startBalance[4]
			hustle.write(startBalanceInfo, "house_trader")
			print("Starting predivider.")

			predivider = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\divider.py', 'logs/bot/predivider{}.txt'.format(time.time())])
			predivider.wait()
			time.sleep(60)
			cur_task['predivider'] = True
			task.seek(0)
			task.truncate()
			json.dump(cur_task, task)
		elif cur_task['predivider'] == True and (cur_task['separator']['user1'] == False or cur_task['separator']['user2'] == False):
			sep1 = False
			sep2 = False
			if cur_task['separator']['user1'] == False:
				print("Starting separator for user1")
				sep1 = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\separator.py', 'user1', 'logs/bot/user1/separator{}.txt'.format(time.time())])
			if cur_task['separator']['user2'] == False:
				print("Starting separator for user2")
				sep2 = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\separator.py', 'user2', 'logs/bot/user2/separator{}.txt'.format(time.time())])
			if sep1 != False and sep2 != False:
				sep1.wait()
				print("sep1 done")
				sep2.wait()
				print("sep2 done")
			else:
				if sep1 == False:
					sep2.wait()
					print("sep2 done")
				else:
					sep1.wait()
					print("sep1 done")

			cur_task['separator']['user1'] = True
			cur_task['separator']['user2'] = True

			with open('tradelist_user1.json', 'r', encoding='utf8') as fa:
				tradelist1 = json.load(fa)
			with open('tradelist_user2.json', 'r', encoding='utf8') as fa:
				tradelist2 = json.load(fa)
			with open('tradelist.json', 'r', encoding='utf8') as fa:
				tradelist = json.load(fa)

			for item in tradelist1:
				tradelist[item] = tradelist1[item]
			for item in tradelist2:
				tradelist[item] = tradelist2[item]

			with open('tradelist.json', 'w', encoding='utf8') as fw:
				json.dump(tradelist, fw)
			with open('tradelist_user1.json', 'w', encoding='utf8') as fw:
				json.dump({}, fw)
			with open('tradelist_user2.json', 'w', encoding='utf8') as fw:
				json.dump({}, fw)

			print("All separators finished work")
			task.seek(0)
			task.truncate()
			json.dump(cur_task, task)
		elif cur_task['keys_exchanger'] == False and cur_task['separator']['user1'] == True and cur_task['separator']['user2'] == True :
			print("Starting key's exchanger.")
			keyex = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\keys_exchanger.py', 'logs/bot/keys_exchanger{}.txt'.format(time.time())])
			keyex.wait()
			cur_task['keys_exchanger'] = True
			task.seek(0)
			task.truncate()
			json.dump(cur_task, task)
		elif cur_task['divider'] == False and cur_task['keys_exchanger'] == True:
			print("Starting divider.")
			divider = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\divider.py', 'logs/bot/divider{}.txt'.format(time.time()), 'empauto'])
			divider.wait()
			cur_task['divider'] = True
			task.seek(0)
			task.truncate()
			json.dump(cur_task, task)
		elif cur_task['divider'] == True and (cur_task['empauto']['user1'] == False or cur_task['empauto']['user2'] == False):
			time.sleep(60)
			emp1 = False
			emp2 = False
			if cur_task['empauto']['user1'] == False:
				print("Starting empauto for user1")
				emp1 = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\empauto.py', 'user1', 'logs/bot/user1/empauto{}.txt'.format(time.time())])
			if cur_task['empauto']['user2'] == False:
				print("Starting empauto for user2")
				emp2 = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\empauto.py', 'user2', 'logs/bot/user2/empauto{}.txt'.format(time.time())])
			if emp1 != False and emp2 != False:
				emp1.wait()
				print("emp1 done")
				emp2.wait()
				print("emp2 done")
			else:
				if emp1 == False:
					emp2.wait()
					print("emp2 done")
				else:
					emp1.wait()
					print("emp1 done")
			cur_task['empauto']['user1'] = True
			cur_task['empauto']['user2'] = True
			print("All empautos finished work")
			task.seek(0)
			task.truncate()
			json.dump(cur_task, task)
		elif cur_task['rolled'] == False and cur_task['empauto']['user1'] == True and cur_task['empauto']['user2'] == True:
			with open('cookies.json', 'r') as f:
				all_cookies = json.load(f)
			roll_sum1 = get_withdraw_info(1, all_cookies["user1"])
			roll_sum2 = get_withdraw_info(2, all_cookies["user2"])
			print(roll_sum1)
			print(roll_sum2)
			if roll_sum1 > 0 or roll_sum2 > 0:
				time.sleep(80)
				roll_sum1 = get_withdraw_info(1, all_cookies["user1"])
				roll_sum2 = get_withdraw_info(2, all_cookies["user2"])
				print(roll_sum1)
				print(roll_sum2)
				if roll_sum1 > 0 or roll_sum2 > 0:
					print("going to bet")
					emp_balance = []
					for USER in all_cookies:
						scraper = cfscrape.create_scraper()
						r= scraper.get('https://csgoempire.com/deposit', headers={'User-Agent': 'Mozilla / 537.36 (KHTML, like Gecko) Chrome /'}, cookies={'__cfduid': all_cookies[USER]['emp']['__cfduid'], 'PHPSESSID': all_cookies[USER]['emp']['PHPSESSID']})
						page = r.content.decode("utf-8")
						start = page.find('<animated-integer v-bind:value="balance" id="balance">') + 54
						end = page.find('</animated-integer>')
						emp_balance.append(float(r.content.decode("utf-8")[start:end]))
					if min(emp_balance[0], emp_balance[1]) <= max(roll_sum1, roll_sum2)+0.05:
						hustle.write("Не гоже більше за банк ставити.", "house_trader")
						raise SystemExit("Bankroll is too low")
						break
					else:
						print("Staison must bet {}$".format(roll_sum1))
						print("Leha must bet {}$".format(roll_sum2))
						if roll_sum1 == 0:
							roll_sum1 = 0.1
						if roll_sum2 == 0:
							roll_sum2 = 0.1
						if (start_rolling(roll_sum1, roll_sum2) == "ok"):
							cur_task['rolled'] = True
							task.seek(0)
							task.truncate()
							json.dump(cur_task, task)
				else:
					cur_task['rolled'] = True
					task.seek(0)
					task.truncate()
					json.dump(cur_task, task)
		elif cur_task['rolled'] == True and (cur_task['withdraw']['user1'] == False or cur_task['withdraw']['user2'] == False):
			with1 = False
			with2 = False
			if cur_task['withdraw']['user1'] == False:
				print("Starting withdraw for user1")
				with1 = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\withdraw.py', 'user1', 'logs/bot/user1/withdraw{}.txt'.format(time.time())])
			if cur_task['withdraw']['user2'] == False:
				print("Starting withdraw for user2")
				with2 = Popen([SYS_EXECUTABLE, os.path.dirname(os.path.abspath(__file__)) + '\\withdraw.py', 'user2', 'logs/bot/user2/withdraw{}.txt'.format(time.time())])
			if with1 != False and with2 != False:
				with1.wait()
				print("with1 done")
				with2.wait()
				print("with2 done")
			else:
				if with1 == False:
					with2.wait()
					print("with2 done")
				else:
					with1.wait()
					print("with1 done")
			cur_task['withdraw']['user1'] = True
			cur_task['withdraw']['user2'] = True
			
			with open('tradelist_user1.json', 'r', encoding='utf8') as fa:
				tradelist1 = json.load(fa)
			with open('tradelist_user2.json', 'r', encoding='utf8') as fa:
				tradelist2 = json.load(fa)
			with open('tradelist.json', 'r', encoding='utf8') as fa:
				tradelist = json.load(fa)

			for item in tradelist1:
				tradelist[item] = tradelist1[item]
			for item in tradelist2:
				tradelist[item] = tradelist2[item]

			with open('tradelist.json', 'w', encoding='utf8') as fw:
				json.dump(tradelist, fw)
			with open('tradelist_user1.json', 'w', encoding='utf8') as fw:
				json.dump({}, fw)
			with open('tradelist_user2.json', 'w', encoding='utf8') as fw:
				json.dump({}, fw)
			
			print("All users withdrawed")
			task.seek(0)
			task.truncate()
			json.dump(cur_task, task)
		elif cur_task['withdraw']['user1'] == True and cur_task['withdraw']['user2'] == True and "start_bankroll" in cur_task:
			startBankroll = cur_task["start_bankroll"]
			time.sleep(30)
			finishBalance = getBalanceInfo()
			del cur_task["start_bankroll"]
			cur_task = {"predivider": False, "separator": {"user1": False, "user2": False}, "keys_exchanger": False, "divider": False, "empauto": {"user1": False, "user2": False}, "rolled": False, "withdraw": {"user1": False, "user2": False}}
			task.seek(0)
			task.truncate()
			json.dump(cur_task, task)
			hustle.write("Колесо сансари дало оборот. Оборот в {}%!".format(int((finishBalance[4]/startBankroll - 1)*10000)/100), "house_trader")
			key_ukr1 = "ключів" if finishBalance[5]['user1'] in range(5, 21) or finishBalance[5]['user1']%100 in range(5, 21) else ("ключ" if finishBalance[5]['user1']%10 == 1 else ("ключа" if finishBalance[5]['user1']%10 == 2 else ("ключі" if finishBalance[5]['user1']%10 in [3,4] else "ключів")))
			key_ukr2 = "ключів" if finishBalance[5]['user2'] in range(5, 21) or finishBalance[5]['user2']%100 in range(5, 21) else ("ключ" if finishBalance[5]['user2']%10 == 1 else ("ключа" if finishBalance[5]['user2']%10 == 2 else ("ключі" if finishBalance[5]['user2']%10 in [3,4] else "ключів")))
			finishBalanceInfo = "Тепер банк - {}$\nStaison підняв {}$ ({}$ на cs.money + {} {} на {}$ і {}$ на empire)\nLeha заробив з {}$ ({}$ на cs.money + {} {} сумарно на {}$ і {}$ на empire)\n".format(finishBalance[4], round(finishBalance[0]+finishBalance[1], 2), round(finishBalance[1]-finishBalance[6]['user1'], 2), finishBalance[5]['user1'], key_ukr1, finishBalance[6]['user1'], finishBalance[0], round(finishBalance[3]+finishBalance[2], 2), round(finishBalance[3]-finishBalance[6]['user2'], 2), finishBalance[5]['user2'], key_ukr2, finishBalance[6]['user2'], finishBalance[2])
			hustle.write(finishBalanceInfo, "house_trader")
			if finishBalance[4] - startBankroll <= 0:
				hustle.write("Ну його, виключаюсь.", "house_trader")
				sys.exit(0)
			time.sleep(10)
		task.close()
		time.sleep(1)