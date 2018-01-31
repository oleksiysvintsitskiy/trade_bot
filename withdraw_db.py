# -*- coding: utf-8 -*-
import os
import time
import json
import pickle
import requests
import cfscrape

MAXPRICE = 200 # in $
UPDATE_TIME = 15 # in seconds

with open('sz_aloner/cookies.json', 'r') as f:
    all_cookies = json.load(f)

hdrs = {'User-Agent': 'Mozilla / 537.36 (KHTML, like Gecko) Chrome /'}
emp_sessions = {
	"methetreedo": {
		"__cfduid": "d44419c5f7355ba2749f56f320003b1124a01493919186",
		"PHPSESSID": "q2p79hhu163mv22217adfee2vrv12"
	},
	"methebus": {
		"__cfduid": "de195b0445483097e153f99901f223291ed41497884650",
		"PHPSESSID": "aol99pp22216rnq4a30flrrs3ijc2"
	},
	"notatreedo": {
		"__cfduid": "d05b6725f8046c526a754f6124140c3d3d961497926440",
		"PHPSESSID": "guv0l9ohj2a5133b5b613a9tdfib7"
	},
	"treaper12k": {
		"__cfduid": "d2b59bf5ee9cc1f6b1242bc12598b41b3d561494688404",
		"PHPSESSID": "4msc4e5poj242220k1dg79afmluv3"
	},
	"sniffesnuffa": {
		"__cfduid": "d964d9e28855e9b3a39d7242b6e1a8836d891497988720",
		"PHPSESSID": "nunlg3vq242fqlk0su315knaur406"
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
			if 'p' in item and item['p'] != 0 and item['p'] >= 0.5 and item['p'] <= MAXPRICE:
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
					output.append([item['m'], int(item['p'] * koef * 1000)])
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
		if 'price' in i:
			price = float(i['price'])
			if price != 0 and price >= 0.5 and price <= MAXPRICE:
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
					output.append([i['name'], int(price * koef * 1000)])
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
			with open('price.pickle', 'rb') as f:
				table = pickle.load(f)
			if time.time()-banList[user] > 60:
				start_time = time.time()
				skins = {}
				empire = []
				scraper = cfscrape.create_scraper()
				sp = scraper.get('https://csgoempire.com/api/get_bot_items', headers=hdrs, cookies=emp_cookie[user])
				mark = sp.content
				prices = mark.decode("utf-8")
				parsed = json.loads(prices)
				tmp_skins = {}
				if parsed['success'] == False:
					banList[user] = time.time()
				else:
					prs = parsed['data']
					check_list = []
					for al in prs:
						empire.append([al['name'], int(al['market_value'] * 10)])
						price = al['market_value'] / 100.
						if price <= MAXPRICE and price >= 0.5:
							if not al['name'] in tmp_skins:
								tmp_skins[al['name']] = 0
							if not al['name'] in skins:
								skins[al['name']] = {'price': price, 'ids': [al['id']]}
							else:
								skins[al['name']]['ids'].append(al['id'])

					for skin in tmp_skins:
						check_list.append({'market_hash_name': skin, 'price': 0.01, 'permission': 'bоth_sіde'})

					data = 'array_items='+json.dumps(check_list)
					cm_cookie = {'Cookie':'__cfduid='+all_cookies['user1']['cm']['__cfduid']+';steamid='+all_cookies['user1']['steamid']+';new_1_csrf='+all_cookies['user1']['cm']['csrf']}
					cm_r = scraper.post('https://cs.money/check_price', headers={'Accept':'*/*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4', 'Connection':'keep-alive', 'Content-Length':'399', 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8', 'Host':'cs.money', 'Origin':'https://cs.money', 'Referer':'https://cs.money/', 'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}, cookies=cm_cookie, data=data)
					cm_res = json.loads(cm_r.content.decode('utf-8'))
					
					for item in cm_res:
						if not item['market_hash_name'] in table:
							table[item['market_hash_name']] = {'CM': '', 'JAR': '', 'EMP': '', 'GG': '', 'TCM': '', 'TEMP': '', 'TGG': '', 'TJAR': ''}
						table[item['market_hash_name']]['CM'] = item['price'] * 968
						table[item['market_hash_name']]['TCM']= time.time()
						# if item['permission'] == 'only_give':
						# 	del skins[item['market_hash_name']]

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
						os.replace('withdraw_db.tmp.json', 'withdraw_db.json')

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

			with open('price.pickle', 'wb') as f:
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