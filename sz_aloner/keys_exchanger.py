import os
import sys
import json
import math
import pickle
import paramiko
import requests
import cfscrape
import threading
import itertools
import time
import time, datetime
from prettytable import PrettyTable
from steampy.client import SteamClient, TradeOfferState, Asset
from steampy.utils import GameOptions, steam_id_to_account_id
import hustle
import logging
from hacks import log as print

def exchange():

	game = GameOptions.CS
	num = 0
	standart = 8000

	logging.basicConfig(format='%(asctime)s | %(message)s', datefmt='%d.%m.%Y %H:%M:%S', filemode='w', filename=sys.argv[1])

	with open('cookies.json', 'r') as f:
		all_cookies = json.load(f)

	hdrs = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br',
								  'accept-language': 'en-US,en;q=0.8,ru;q=0.6,uk;q=0.4',
								  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
								  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
								  'x-requested-with': 'XMLHttpRequest'}

	cfduid1 = all_cookies['user1']['cm']['__cfduid']
	steamid1 = all_cookies['user1']['steamid']
	new_1_csrf1 = all_cookies['user1']['cm']['csrf']

	cfduid2 = all_cookies['user2']['cm']['__cfduid']
	steamid2 = all_cookies['user2']['steamid']
	new_1_csrf2 = all_cookies['user2']['cm']['csrf']

	cookies1 = {'Cookie':'__cfduid='+cfduid1+';steamid='+steamid1+';new_1_csrf='+new_1_csrf1}
	trade_url1 = all_cookies['user1']['emp']['trade_url']

	cookies2 = {'Cookie':'__cfduid='+cfduid2+';steamid='+steamid2+';new_1_csrf='+new_1_csrf2}
	trade_url2 = all_cookies['user2']['emp']['trade_url']

	def get_own_items1(output):
		_sum = 0
		while(True):
			output[:]=[]
			_sum = 0
			try:
				scraper = cfscrape.create_scraper()
				sp = scraper.get('https://cs.money/load_inventory?hash='+str(int(time.time()*1000)), headers=hdrs, cookies=cookies1)
				mark = sp.content
				prices = mark.decode("utf-8")
				prs = json.loads(prices)
				print(prs)
				for al in prs:
					if al.get('a') != "only_give" and al['t']!='ky':
						output.append([al['m'], int(round(float(al['p']*(al['r']+2)/100),2)*100), str(al['id'])])
						_sum += int(round(float(al['p']*(al['r']+2)/100)*100,2))
				break
			except Exception as e:
				print("Couldn't load user1 inventory.")
				print(e)
		return _sum

	def get_own_items2(output):
		_sum = 0
		while(True):
			output[:]=[]
			_sum = 0
			try:
				scraper = cfscrape.create_scraper()
				sp = scraper.get('https://cs.money/load_inventory?hash='+str(int(time.time()*1000)), headers=hdrs, cookies=cookies2)
				mark = sp.content
				prices = mark.decode("utf-8")
				prs = json.loads(prices)
				for al in prs:
					if al.get('a') != "only_give" and al['t']!='ky':
						output.append([al['m'], int(round(float(al['p']*(al['r']+2)/100),2)*100), str(al['id'])])
						_sum += int(round(float(al['p']*(al['r']+2)/100)*100,2))
				break
			except Exception as e:
				print("Couldn't load user1 inventory.")
				print(e)
		return _sum

	def get_cm_prices(bots_cm_id):
		while(True):
			try:
				output = []
				bots_cm_name = []
				with open('tradelist.json', 'rb') as fa:
					try:
						tradelist = json.load(fa)
					except EOFError:
						tradelist = []
				scraper = cfscrape.create_scraper()
				sp = scraper.get('https://cs.money/load_all_bots_inventory', headers=hdrs)
				mark = sp.content
				prices = mark.decode("utf-8")
				prs = json.loads(prices)
				for bot in prs:
					bots_cm_name.append(bot)
					bots_cm_id.append('')
				for bot in range(len(bots_cm_name)):
					items = []
					all = prs.get(bots_cm_name[bot])
					if all:
						for al in all:
							bots_cm_id[bot] = str(al['b'])
							if al['m'].find('Case Key')>0 and al['m'].find("CS:GO")==-1:
								tradelist[al['m']] = 'to_money'
								items.append([al['m'], int(al['p']*100), str(al['id'])])
					output.append(items)
				with open('tradelist.json', 'w') as f:
					json.dump(tradelist, f)
				break
			except Exception as e:
				print("Zaebali cm prices")
				print(e)
		return output

	user1_output = []
	user2_output = []
	user1_sum = get_own_items1(user1_output)
	user2_sum = get_own_items2(user2_output)
	bots_cm_id = []
	cm_prices = get_cm_prices(bots_cm_id)

	print("Got all users + bots inventories")
	if user1_sum + user2_sum < standart:
		hustle.write('Ключі поки що не виводжу.', "house_trader")
		raise SystemExit("no_dividing")

	max_keys = 0
	bot_num = 0
	for i in range(len(bots_cm_id)):
		if len(cm_prices[i])>max_keys:
			max_keys = len(cm_prices[i])
			bot_num = i

	most_keyable = cm_prices[bot_num]

	bot_id = bots_cm_id[bot_num]

	print("id " + str(bot_id) + " gonna exchange with us.")

	# most_keyable = sorted(most_keyable, key=lambda x: x[1])

	if user1_sum + user2_sum - standart >=900:
		num = int((user1_sum + user2_sum - standart)/300)
	else:
		num = 2

	print((user1_sum + user2_sum)/100, "$  joint balance. Gonna exchange {} keys.".format(num))

	keys = []
	keys_sum = 0

	for i in range(num):
		keys.append(most_keyable[i][2])
		keys_sum = keys_sum + most_keyable[i][1]


	def findanswer(res_deal):

		price = []

		W = 0
		n = 0

		for i in range(len(items)):
			price.append(items[i][1])

		W = keys_sum
		n = len(items)

		K = [[0 for x in range(W+1)] for x in range(n+1)]

		for i in range(n+1):
			for w in range(W+1):
				if i==0 or w==0:
					K[i][w] = 0
				elif price[i-1] <= w:
					K[i][w] = max(int(price[i-1] + K[i-1][w-price[i-1]]),  int(K[i-1][w]))
				else:
					K[i][w] = K[i-1][w]

		cost = 0

		def findans(i, j):
			nonlocal cost
			if K[i][j] == 0:
				return
			if K[i-1][j] == K[i][j]:
				findans(i-1, j)
			else:
				findans(i-1, j-price[i-1])
				cost += price[i-1]
				res_deal.append(i-1)

		findans(n, W)

		return cost
		

	if user1_sum > user2_sum:
		cookies = cookies1
		items = user1_output
		USER = "user1"
		USER1 = "user2"
	else:
		cookies = cookies2
		items = user2_output
		USER = "user2"
		USER1 = "user1"

	ind = []

	cost = findanswer(ind)
	if cost > 0:
		print("Successfully found answer. Preparing for sending offer.")

	scraper = cfscrape.create_scraper() 
	headers = {'Accept':'*/*','Accept-Encoding':'gzip, deflate, br','Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,uk;q=0.2','Connection':'keep-alive', 'Content-Length':'118', 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','DNT':'1','Host':'cs.money','Origin':'https://cs.money','Referer':'https://cs.money/','User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36', 'X-Requested-With':'XMLHttpRequest'} 
	peopleItems = []
	for i in ind:	
		peopleItems.append(items[i][2])
	data = "steamid="+bot_id+"&botItems="+json.dumps(keys)+"&peopleItems="+json.dumps(peopleItems)+'&userSum='+str(cost)+'&botSum='+str(keys_sum)
	r = scraper.post('https://cs.money/send_offer', data = data, cookies = cookies, headers = headers)
	if r.text == 'OK':
		hustle.write('Вивели {} ключа на акаунті {} (но это не точно).'.format(num, USER), "house_trader")
		print("Offer was sent.")
		time.sleep(120)
		raise SystemExit("ok")

if __name__ == "__main__":
	tries = 0
	while True:
		try:
			tries += 1
			exchange()
		except SystemExit as e:
			if str(e) == "no_dividing":
				break
			elif str(e) == "ok":
				break
		except:
			print('error')
			if tries == 3:
				hustle.write('З поділу ключів вийшли ексепшном.', "house_trader")
				raise