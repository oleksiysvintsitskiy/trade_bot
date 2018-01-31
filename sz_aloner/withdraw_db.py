# -*- coding: utf-8 -*-
import os
import time
import json
import pickle
import requests
import cfscrape

maxprice = 200 # in $
UPDATE_TIME = 15 # in seconds

hdrs = {'User-Agent': 'Mozilla / 537.36 (KHTML, like Gecko) Chrome /'}
emp_sessions = {
	"methetreedo": {
		"__cfduid": "d44419c5f7355ba0749f56f320003b4a01493919186",
		"PHPSESSID": "q2p79hhu163mv17adfee2vrv12"
	},
	"methebus": {
		"__cfduid": "de195b0445483097ef53f99901f291ed41497884650",
		"PHPSESSID": "aol99pp16rnq4a30flrrs3ijc2"
	},
	"notatreedo": {
		"__cfduid": "d05b6725f8046c526ad54f6140c3d3d961497926440",
		"PHPSESSID": "guv0l9ohj2a54b5b61a9tdfib7"
	},
	"treaper12k": {
		"__cfduid": "d2b59bf5ee9cc1f6b1bc12598b41b3d561494688404",
		"PHPSESSID": "4msc4e5poj220k1dg79afmluv3"
	},
	"sniffesnuffa": {
		"__cfduid": "d964d9e28855e9b3a39d7b6e1a8836d891497988720",
		"PHPSESSID": "nunlg3vqfqlk0su315knaur406"
	}
}

def get_cm_prices(output):
	scraper = cfscrape.create_scraper()
	sp = scraper.get('https://cs.money/load_all_bots_inventory', headers=hdrs)
	mark = sp.content
	prices = mark.decode("utf-8")
	prs = json.loads(prices)
	for bot in prs:
		for item in prs[bot]:
			if 'p' in item and float(item['p']) != 0 and float(item['p']) >= 0.5 and float(item['p']) <= maxprice:
				koef = 1
				if item['t'] == 'ky':
					koef = 102/105.
				elif (item['t'] == 'k' or item['t'] == 'gw'):
					koef = .97
				elif item['t'] == 'w':
					koef = 92/95.
				elif item['t'] == 'm':
					koef = 87/90.
				if koef != 1:
					output.append([item['m'], int(float(item['p']) * koef * 1000)])
	return

def get_jar_prices(output):
	scraper = cfscrape.create_scraper()
	sp = scraper.get('https://skinsjar.com/api/v3/load/bots?refresh=1&v=2', headers=hdrs)
	mark = sp.content
	prices = mark.decode("utf-8")
	prs = json.loads(prices)
	min_id = 0
	min_bot = 0
	min_name = ''
	for i in prs["items"]:
		if 'price' in i and float(i['price']) != 0 and float(i['price']) >= 0.5 and float(i['price']) <= maxprice:
			koef = 1
			if i['category'] == 'Key':
				koef = 1005/1025.
			elif i['category'] == 'Knife':
				koef = 965/985.
			elif i['category'] == 'Sticker' or i['category'] == 'Tag' or i['category'] == 'Gloves' or i['category'] == 'Pin' or i['category'] == 'Music Kit':
				koef = 865/885.
			else:
				koef = 915/935.

			if koef != 1:
				koef -= 0.0123 #experimental
				output.append([i['name'], int(float(i['price']) * koef * 1000)])
	return

emp_cookie = {}
banList = {}

for user in emp_sessions:
	emp_cookie[user] = {'__cfduid': emp_sessions[user]['__cfduid'], 'PHPSESSID': emp_sessions[user]['PHPSESSID']}
	banList[user] = 0

updates = 0

while True:
	for user in emp_sessions:
		try:
			with open('../price.pickle', 'rb') as f:
				table = pickle.load(f)
			if time.time()-banList[user] > 60:
				start_time = time.time()
				skins = {}
				empire = []
				with open('logs/overstock_db.json', 'rb') as f:
					overstock = json.load(f)
				scraper = cfscrape.create_scraper()
				sp = scraper.get('https://csgoempire.com/api/get_bot_items', headers=hdrs, cookies=emp_cookie[user])
				mark = sp.content
				prices = mark.decode("utf-8")
				parsed = json.loads(prices)
				if parsed['success'] == False:
					banList[user] = time.time()
				else:
					prs = parsed['data']
					for al in prs:
						empire.append([al['name'], int(al['market_value'] * 10)])
						price = int(al['market_value']) / 100.
						if price <= maxprice and price >= 0.5:
							if al['name'] in overstock:
								if overstock[al['name']]['status'] == 'both_side':
									if not al['name'] in skins:
										skins[al['name']] = {'price': price, 'ids': [al['id']]}
									else:
										skins[al['name']]['ids'].append(al['id'])
							else:
								if not al['name'] in skins:
									skins[al['name']] = {'price': price, 'ids': [al['id']]}
								else:
									skins[al['name']]['ids'].append(al['id'])

					for item in empire:
						if not item[0] in table:
							table[item[0]] = {'CM': '', 'JAR': '', 'EMP': '', 'GG': '', 'TCM': '', 'TEMP': '', 'TGG': '', 'TJAR': ''}
						table[item[0]]['EMP'] = item[1]
						table[item[0]]['TEMP']= time.time()

					dump_success = False
					with open('withdraw_db.tmp.json', 'w', encoding='utf8') as f:
						try:
							json.dump(skins, f)
							dump_success = True
						except BaseException as e:
							print("#0", e)
					if dump_success == True:
						os.replace('withdraw_db.tmp.json', '../withdraw_db.json')

			cm = []
			jar = []
			get_cm_prices(cm)
			for item in cm:
				if not item[0] in table:
					table[item[0]] = {'CM': '', 'JAR': '', 'EMP': '', 'GG': '', 'TCM': '', 'TEMP': '', 'TGG': '', 'TJAR': ''}
				table[item[0]]['CM'] = item[1]
				table[item[0]]['TCM'] = time.time()

			# get_jar_prices(jar)
			# for item in jar:
			# 	if not item[0] in table:
			# 		table[item[0]] = {'CM': '', 'JAR': '', 'EMP': '', 'GG': '', 'TCM': '', 'TEMP': '', 'TGG': '', 'TJAR': ''}
			# 	table[item[0]]['JAR'] = item[1]
			# 	table[item[0]]['TJAR'] = time.time()

			with open('../price.pickle', 'wb') as f:
				pickle.dump(table, f)
				
			if updates % 10 == 0:
				# print("Successful update at ", time.strftime("|%H:%M|"))
				updates = 0
			print("Successful update at ", time.strftime("|%H:%M|"))
			updates += 1

			if time.time()-start_time < UPDATE_TIME:
				time.sleep(UPDATE_TIME-(time.time()-start_time))

		except BaseException as e:
			print("#1", e)