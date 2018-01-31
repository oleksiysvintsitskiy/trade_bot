# -*- coding: utf-8 -*-
import os
import sys
import json
import math
import pickle
import requests
import itertools
import time
import datetime
import json
import cfscrape
import threading
import logging
import hustle
from urllib.parse import quote
from steampy.client import SteamClient
from hacks import log as print

def checko(item_name): #проверка наличия в оверстоке при обмене на СМ (True если нету в бд)
	market_hash_name = quote(item_name, safe='')
	scraper = cfscrape.create_scraper()
	for i in range(5):
		try:
			p = scraper.get('https://cs.money/check_item_status?market_hash_name='+market_hash_name, headers=hdrs)
			if p.text == 'OK':
				return True 
			return False
		except Exception as e:
			print(e)
			time.sleep(1)
	return False

logging.basicConfig(format='%(asctime)s | %(message)s', datefmt='%d.%m.%Y %H:%M:%S', filemode='w', filename=sys.argv[2])

USER = sys.argv[1]
banList = []
HAVE_ACTIVE = 0

with open('cookies.json', 'r') as f:
	all_cookies = json.load(f)

emp_cookie = {'__cfduid': all_cookies[USER]['emp']['__cfduid'], 'PHPSESSID': all_cookies[USER]['emp']['PHPSESSID']}
hdrs = {'User-Agent': 'Mozilla / 537.36 (KHTML, like Gecko) Chrome /'}
hd = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br',
				  'accept-language': 'en-US,en;q=0.8,ru;q=0.6,uk;q=0.4',
				  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
				  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
				  'x-requested-with': 'XMLHttpRequest'}

with open(USER+'.pickle', 'rb') as f:
	client = pickle.load(f)

if not client.is_session_alive():
	client = SteamClient(all_cookies[USER]['api'])
	attemts = 0
	print('Trying to login '+USER)
	while (1):
		if attemts == 3:
			hustle.write("Перезагрузи роутер, дядя. (too many try_logins on empauto user1)", "house_trader")
			time.sleep(40)
		try:
			print('Try login user1')
			client.login(all_cookies[USER]['username'], all_cookies[USER]['password'], all_cookies[USER]['sgpath'])
		except Exception as e:
			attemts += 1
			print(e)
			time.sleep(10)
			continue
		else:
			break
	print(USER+' was logged in successfully')
	with open(USER+'.pickle', 'wb') as f:
		pickle.dump(client, f)

def decline_all_offers():
	global client
	for i in range(3):
		try:
			print('Starting {} attempt to decline all offers'.format(i+1))
			offers = []
			now = time.time()
			while time.time() - now < 10 and len(offers) == 0:
				time.sleep(2)
				offers = client.get_trade_offers()['response']['trade_offers_received']
			if len(offers) != 0:
				print('Found {} offers'.format(len(offers)))
				for offer in offers:
					client.decline_trade_offer(offer['tradeofferid'])
					print('Declined offer')
				break
		except Exception as e:
			print('decline_all_offers error:', e)

def get_cm_prices(skins):
	global best_item
	print("Getting cs.money items")
	
	best_profit = -1e+10

	while True:
		try:
			with open('../price.pickle', 'rb') as f:
				table = pickle.load(f)
			for item in table:
				if item in skins:
					if table[item]['CM'] != '':
						if time.time() - table[item]['TCM'] < 3600 * 6:
							if not 'cm_price' in skins[item]:
								price = float(table[item]['CM']) / 1000
								skins[item]['cm_price'] = price
								tmp_profit = price/skins[item]['price']-1
								if price/skins[item]['price'] >= 1.13:
									if checko(item):
										if tmp_profit > best_profit:
											best_profit = tmp_profit
											best_item = item
										elif tmp_profit == best_profit and skins[item]['price'] > skins[best_item]['price']:
											best_item = item
			break
		except BaseException as e:
			print(e)
			time.sleep(5)

	return
'''
def get_cm_prices(skins):
	global best_item
	print("Getting cs.money items")
	
	best_profit = -1e+10

	scraper = cfscrape.create_scraper()
	sp = scraper.get('https://cs.money/load_all_bots_inventory', headers=hdrs)
	mark = sp.content
	prices = mark.decode("utf-8")
	prs = json.loads(prices)
	for bot in prs:
		for item in prs[bot]:
			if item['m'] in skins:
				if item['p'] != 0:
					if not 'cm_price' in skins[item['m']]:
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
							price = item['p'] * koef
							skins[item['m']]['cm_price'] = price
							tmp_profit = price/skins[item['m']]['price']-1
							if tmp_profit > best_profit:
								best_profit = tmp_profit
								best_item = item['m']
							elif tmp_profit == best_profit and skins[item['m']]['price'] > skins[best_item]['price']:
								best_item = item['m']
	return
'''
def get_empire_prices(maxprice):
	global banList
	skins = {}
	print("Getting csgoempire.com items")
	while True:
		try:
			with open('../withdraw_db.json', 'r') as f:
				skins_db = json.load(f)
			for skin in skins_db:
				if skins_db[skin]['price'] <= maxprice:
					for skin_id in skins_db[skin]['ids']:
						if not int(skin_id) in banList:
							if skin.find("Key") == -1:
								if not skin in skins:
									skins[skin] = {'price': skins_db[skin]['price'], 'ids': [skin_id]}
								else:
									skins[skin]['ids'].append(skin_id)
			# with open('nodejs/overstock.json', 'rb') as f:
			# 	overstock = json.load(f)
			# sp = requests.get('https://csgoempire.com/api/get_bot_items', headers=hdrs, cookies=emp_cookie)
			# mark = sp.content
			# prices = mark.decode("utf-8")
			# parsed = json.loads(prices)
			# if parsed['success'] == False:
			# 	time.sleep(180)
			# else:
			# 	prs = parsed['data']['items']
			# 	for al in prs:
			# 		price = al['market_value'] / 100.
			# 		if price <= maxprice and price >= 3.5:
			# 			if not (int(al['asset_id']) in banList):
			# 				if al['market_name'] in overstock:
			# 					if overstock[al['market_name']]['status'] == 'both_side':
			# 						if not al['market_name'] in skins:
			# 							skins[al['market_name']] = {'price': price, 'ids': [al['asset_id']]}
			# 						else:
			# 							skins[al['market_name']]['ids'].append(al['asset_id'])
			# 				else:
			# 					if not al['market_name'] in skins:
			# 						skins[al['market_name']] = {'price': price, 'ids': [al['asset_id']]}
			# 					else:
			# 						skins[al['market_name']]['ids'].append(al['asset_id'])

			break
		except BaseException as e:
			print(e)
		except:
			print("unknown error")
	return skins

best_item = ""

def withdraw():

	global best_item, balance, banList, HAVE_ACTIVE
	trade_url = "trade_url="+all_cookies[USER]['tradelink']

	print("Loading empire balance")
	scraper = cfscrape.create_scraper()
	r = scraper.get('https://csgoempire.com/deposit', headers=hdrs, cookies=emp_cookie)
	page = r.content.decode("utf-8")
	start = page.find('<animated-integer v-bind:value="balance" id="balance">') + 54 # len('<animated-integer v-bind:value="balance" id="balance">') == 54
	end = page.find('</animated-integer>')
	balance = float(r.content.decode("utf-8")[start:end])
	print("Balance: {}$".format(balance))
	if balance <= 7.0:
		hustle.write(('Льоха' if USER == 'user2' else 'Стасян')+" зробив круг!", "house_trader")
		raise SystemExit("ok")
	best_item = ""
	skins = get_empire_prices(balance)
	get_cm_prices(skins)
	#if skins[best_item]['cm_price'] - skins[best_item]['price'] < 0:
	if best_item == "":
		print(best_item.encode("utf-8"), " bad profit")
		time.sleep(10)
		sys.exit(4)
	
	print("{} ({}%)".format(best_item.encode("utf-8"), round((skins[best_item]['cm_price']/skins[best_item]['price'] - 1) * 100, 2)))
	while True:
		try:
			with open('tradelist_'+USER+'.json', 'rb') as fa:
				tradelist = json.load(fa)
				print(best_item.encode("utf-8"),"->",'for_parse')
				tradelist[best_item] = 'for_parse'
				with open('tradelist_'+USER+'.json', 'w') as fw:
					json.dump(tradelist, fw)
			print("added to "+'tradelist_'+USER+'.json')
			break
		except BaseException as e:
			print(e)
			time.sleep(5)
		except:
			print("unknown error")
			time.sleep(5)

	trade_ok = False

	s = requests.Session()
	s.cookies.update(emp_cookie)
	setOffer = s.post('https://csgoempire.com/api/set_trade_url', data=trade_url, headers=hd)
	print("set_trade_url:", setOffer.content)
	print("Trying withdraw one of {} items".format(len(skins[best_item]['ids'])))

	while balance > 7.0:
		print("banlist:", banList)
		for i in skins[best_item]['ids']:
			if not trade_ok:
				try:
					code = 0
					drawQuery = 'transfer_type=withdraw&item_ids%5B%5D='+str(i)
					print('query:', drawQuery)
					try:
						print("Try send", i)
						drawOffer = s.post('https://csgoempire.com/api/transfer_items', data=drawQuery, headers=hd)
						print("transfer_items: ", drawOffer.content)
						drawJson = json.loads(drawOffer.content.decode("utf-8"))
						if not 'code' in drawJson:
							if 'message' in drawJson:
								if drawJson['message'] == 'You already have an active trade offer.':
									HAVE_ACTIVE += 1
									if HAVE_ACTIVE > 4:
										decline_all_offers()
								else:
									HAVE_ACTIVE = 0
									if drawJson['message'] == 'One or more items are invalid or no longer exist in the inventory.':
										print("one or more...")
										banList.append(i)
										print(banList)
									elif drawJson['message'] == 'Not enough credits to withdraw.':
										sys.exit(4) 
									
							time.sleep(20)
							break
						code = drawJson['code']
						print('offer code:', code)
					except BaseException as e:
						print(e)

					'''
					if code == 0:
						continue
					print("Trying to accept offer", code)
					url = 'https://csgoempire.com/api/check_transfer?transfer_type=withdraw&code='+str(code)
					dt = 'transfer_type=withraw&code='+str(code)
					offer_id = ''

					start = time.time()
					while(time.time()-start < 25):
						try:
							print('Try check')
							processing = 0
							while (offer_id == ''):
								if processing >= 5:
									break
								checkOffer = s.post(url, data=dt, headers=hd)
								transf_obj = json.loads(checkOffer.content.decode("utf-8"))
								print("check_transfer: ", checkOffer.content)
								if transf_obj['success'] == False:
									print('BAN')
									#banList.append(i)
									break
								else:
									if transf_obj['data']['status'] == 'sent':
										offer_id = transf_obj['data']['offer_id']
										print(offer_id)
									elif transf_obj['data']['status'] == 'processing':
										processing += 1
								if offer_id == '':
									time.sleep(2)
							trade_ok = True
							break
						except KeyError:
							continue
						else:
							break

					time.sleep(5)
					'''
				except KeyError:
					continue
				else:
					break
			else:
				trade_ok = False
				break
		time.sleep(4)
		scraper = cfscrape.create_scraper()
		r = scraper.get('https://csgoempire.com/deposit', headers=hdrs, cookies=emp_cookie)
		page = r.content.decode("utf-8")
		start = page.find('<animated-integer v-bind:value="balance" id="balance">') + 54 # len('<animated-integer v-bind:value="balance" id="balance">') == 54
		end = page.find('</animated-integer>')
		balance = float(r.content.decode("utf-8")[start:end])
		if balance > 1:
			skins.clear()
			best_item = ""
			skins = get_empire_prices(balance)
			get_cm_prices(skins)
			if skins[best_item]['cm_price'] - skins[best_item]['price'] < 0:
				sys.exit(4)
			print("{} ({}%)".format(best_item.encode("utf-8"), round((skins[best_item]['cm_price']/skins[best_item]['price'] - 1) * 100, 2)))
			while True:
				try:
					with open('tradelist_'+USER+'.json', 'rb') as fa:
						tradelist = json.load(fa)
						print(best_item.encode("utf-8"),"->",'for_parse')
						tradelist[best_item] = 'for_parse'
						with open('tradelist_'+USER+'.json', 'w') as fw:
							json.dump(tradelist, fw)
					print("added to "+'tradelist_'+USER+'.json')
					break
				except BaseException as e:
					print(e)
					time.sleep(5)
				except:
					print("unknown error")
					time.sleep(5)
			trade_ok = False

if __name__ == '__main__':
	while True:
		try:
			withdraw()
		except SystemExit as e:
			if str(e) == "ok":
				break
			print(e)
		except BaseException as e:
			print(e)
		except:
			print("unknown error")