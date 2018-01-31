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
from math import floor
from prettytable import PrettyTable
from knapsack import knapsack
from steampy.client import SteamClient, TradeOfferState, Asset
from steampy.utils import GameOptions, steam_id_to_account_id
import hustle
import logging
from hacks import log as print

try:

	ignored_items = []
	ignored = False
	MIN_PRICE = 600
	MAX_PRICE = 3200
	BAG_SIZE = 1600
	LIM_PRICE = 1300

	logging.basicConfig(format='%(asctime)s | %(message)s', datefmt='%d.%m.%Y %H:%M:%S', filemode='w', filename=sys.argv[2])
	USER = sys.argv[1]
	print("Inited separator for "+USER)
	
	client = 0

	with open('cookies.json', 'r') as f:
		all_cookies = json.load(f)

	hdrs = {'User-Agent': 'Mozilla / 537.36 (KHTML, like Gecko) Chrome /'}

	cfduid = all_cookies[USER]['cm']['__cfduid']
	steamid = all_cookies[USER]['steamid']
	new_1_csrf = all_cookies[USER]['cm']['csrf']

	items_price = int(0)
	
	api_key = all_cookies[USER]['api']
	steamguard_path = all_cookies[USER]['sgpath']
	username = all_cookies[USER]['username']
	password = all_cookies[USER]['password']

	bots_info = {}

	bots_cm_name = []
	bots_cm_id = []

	def get_own_items():
		output = []
		tmp_out = []
		global ignored, ignored_items
		while True:
			try:
				output[:] = []
				tmp_out[:] = []
				with open('tradelist.json', 'r', encoding="utf8") as fa:
					try:
						tradelist = json.load(fa)
					except EOFError:
						tradelist = []
					except BaseException as e:
						print("#0", e)
				with open('tradelist_'+USER+'.json', 'r', encoding="utf8") as fa:
					try:
						tradelist_user = json.load(fa)
					except EOFError:
						tradelist_user = []
					except BaseException as e:
						print("#1", e)
				for tmp_item in tradelist_user:
					tradelist[tmp_item] = tradelist_user[tmp_item]
				cookie = {'Cookie':'__cfduid='+cfduid+';steamid='+steamid+';new_1_csrf='+new_1_csrf}
				sp = requests.get('https://cs.money/load_inventory', headers=hdrs, cookies=cookie)
				mark = sp.content
				prices = mark.decode("utf-8")
				if mark[0:7] != '"Error_':
					prs = json.loads(prices)
					for al in prs:
						if not al['id'] in ignored_items:
							if al['m'] in tradelist:
								if tradelist[al['m']] == 'for_parse':
									if al['p'] != 0 and al.get('a') != "only_give":
										item_price = int(round(float(al['p']*(al['r']+2)/100), 2)*100)
										tmp_out.append([al['m'], item_price, str(al['id'])])
										if item_price > MAX_PRICE:
											output.append(tmp_out[-1])
											break
										elif item_price in range(BAG_SIZE, MAX_PRICE+1):# and len(tmp_out) == 1:
											output.append(tmp_out[-1])
											break
						else:
							print("Ignored items: {}".format(ignored_items))
							ignored = True
					#for it in tmp_out:
					if len(tmp_out) == 0:
						if ignored == False:
							hustle.write(('Staison' if sys.argv[1] == 'user1' else 'Leha')+" розпарсив на емп.", "house_trader")
							raise SystemExit("ok")
					elif len(output) == 0:
						#result = knapsack(MAX_SIZE-1, *[[tmp_out[i][1] for i in range(len(tmp_out))] for j in range(2)], len(tmp_out))
						result = knapsack(BAG_SIZE-1, *[[tmp_out[i][1] for i in range(len(tmp_out))] for j in range(2)], len(tmp_out))
						output = [tmp_out[i] for i in result[1]]
					break
				else:
					time.sleep(10)
			except SystemExit as e:
				raise
			except BaseException as e:
				print(e)
				time.sleep(5)
			except:
				print("unknown error in get_own_items")
		return output

	def get_cm_prices():
		output = []
		bots_cm_name = []
		bots_cm_id = []
		global items_price
		while True:
			try:
				output[:] = []
				sp = requests.get('https://cs.money/load_all_bots_inventory', headers=hdrs)
				mark = sp.content
				prices = mark.decode("utf-8")
				prs = json.loads(prices)
				if len(bots_cm_name) < 24:
					bots_cm_name[:] = []
					bots_cm_id[:] = []
					for bot in prs:
						bots_cm_name.append(bot)
						bots_cm_id.append('')
				for bot in range(len(bots_cm_name)):
					items = []
					all = prs.get(bots_cm_name[bot])
					if all:
						for al in all:
							if int(al.get('p')*100) != 0 and int(al.get('p')*100) <= items_price and int(al.get('p')*97) > 100:
								#print(al.get('p'))
								bots_cm_id[bot] = str(al.get('b'))
								items.append([al.get('m'), int(al.get('p')*100), str(al.get('id'))])
					output.append(items)
				break
			except BaseException as e:
				print(e)
				print("error")
				time.sleep(5)
		return output, bots_cm_name, bots_cm_id

	def get_em_prices():
		output = []
		global items_price
		while True:
			try:
				output[:] = []
				with open('../price.pickle', 'rb') as f:
					table = pickle.load(f)
				for item in table:
					if (table[item]['EMP'] != '') and int(table[item]['EMP']/10) <= items_price and int(table[item]['EMP']/10) > 100:
						output.append([item, int(table[item]['EMP']/10)])
				break
			except BaseException as e:
				print(e)
				time.sleep(5)
		return output

	def get_cm_items():
		output = []
		
		em_prices = []
		cm_prices = []

		em_prices = get_em_prices()
		print('Got emp prices')
		cm_prices_res = get_cm_prices()
		cm_prices = cm_prices_res[0]
		bots_cm_name = cm_prices_res[1]
		bots_cm_id = cm_prices_res[2]
		print('Got cm prices')
		for i in range(len(bots_cm_name)):
			ans = []
			for j in range(len(cm_prices[i])):
				for k in range(len(em_prices)):
					if cm_prices[i][j][0] == em_prices[k][0] and em_prices[k][1] > 100:
						ans.append([cm_prices[i][j][2], cm_prices[i][j][1], em_prices[k][1], cm_prices[i][j][0]])
			output.append(ans)
		return output, bots_cm_name, bots_cm_id

	def get_bot_id():
		while True:
			bots_info = {}
			try:
				sp = requests.get('https://cs.money/get_info', headers=hdrs)
				mark = sp.content
				info = mark.decode("utf-8")
				bots = json.loads(info).get('list_bots')
				for bot in bots:
					bots_info[bot['name']] = bot['steamid']
					#print(bot['steamid'])
					#print(str(steam_id_to_account_id(str(bot['steamid']))))
				break
			except:
				print("Getting bot id error")
				time.sleep(3)
		return bots_info

	def main():
		global items_price
		global ignored, ignored_items

		bots_cm_name = []
		bots_cm_id = []

		bots_info = get_bot_id()
		print("Got bots")
		#print("Get user")
		
		flag = 0
		own_items = []
		cm_items = []

		while True:
			print("\n")
			own_items[:] = []
			cm_items[:] = []
			print("Start")
			own_items = get_own_items()
			print("Got {} own items".format(len(own_items)))

			if len(own_items) == 0:
				if ignored == True:
					ignored = False
					ignored_items[:] = []
					time.sleep(8)
					continue
				else:
					break

			if len(own_items) == 1 and own_items[0][1] > MAX_PRICE:
				large_price = own_items[0][1]
				output = []
				bots_small = {}
				while True:
					try:
						output[:] = []
						bots_small = {}
						sp = requests.get('https://cs.money/load_all_bots_inventory', headers=hdrs)
						mark = sp.content
						prices = mark.decode("utf-8")
						prs = json.loads(prices)
						for bot in prs:
							small = []
							for al in prs[bot]:
								if not al['b'] in bots_small:
									bots_small[al['b']] = []
								if int(al.get('p')*96) in range(100, LIM_PRICE): # int(al.get('p')*100) != 0 and int(MIN_PRICE/2 + MAX_PRICE/2) and int(al.get('p')*97) > 150:
									#print(al.get('p'))
									bots_small[al['b']].append([al.get('m'), int(al.get('p')*100), str(al.get('id'))])
						break
					except BaseException as e:
						print(e)
						print("error")
						time.sleep(5)
				best_price = -1e+10
				deal_bot = 0
				best_deal = []
				for bot in bots_small:
					result = knapsack(large_price-1, *[[bots_small[bot][i][1] for i in range(len(bots_small[bot]))] for j in range(2)], len(bots_small[bot]))
					if abs(result[0] - large_price) <= 1:
						best_price = result[0]
						best_deal = result[1]
						deal_bot = bot
						break
					if result[0] > best_price:
						best_price = result[0]
						best_deal = result[1]
						deal_bot = bot

				cookies = {'cookie': all_cookies[USER]['cm']['cookie']}
				headers = {'Accept':'*/*','Accept-Encoding':'gzip, deflate, br','Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,uk;q=0.2','Connection':'keep-alive', 'Content-Length':'118', 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','DNT':'1','Host':'cs.money','Origin':'https://cs.money','Referer':'https://cs.money/','User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36', 'X-Requested-With':'XMLHttpRequest'} 
				scraper = cfscrape.create_scraper()

				print('-------***', deal_bot, '***-------')
				bot_sum = float(sum([bots_small[deal_bot][i][1] for i in best_deal])/100)
				data = "steamid="+deal_bot+"&botItems="+json.dumps([str(bots_small[deal_bot][i][2]) for i in best_deal])+"&peopleItems="+json.dumps([str(own_items[i][2]) for i in range(len(own_items))])+'&userSum='+str(sum([float(own_items[i][1]/100.) for i in range(len(own_items))]))+'&botSum='+str(bot_sum)
				r = scraper.post('https://cs.money/send_offer', data = data, cookies = cookies, headers = headers)
				if r.text == 'OK':
					with open('tradelist_'+USER+'.json', 'r', encoding="utf8") as fa:
						try:
							tradelist = json.load(fa)
						except EOFError:
							tradelist = {}

						for i in best_deal:
							item_name = str(bots_small[deal_bot][i][0])
							if not item_name in tradelist:
								print(item_name.encode("utf-8"), " -> for_parse")
							tradelist[item_name] = 'for_parse'
						with open('tradelist_'+USER+'.json', 'w') as fw:
							json.dump(tradelist, fw)
					print('added to tradelist_'+USER+'.json')

					ignored_new = [str(own_items[i][2]) for i in range(len(own_items))]
					ignored_items.extend(ignored_new)
					ignored = False
				else:
					print(r.text)
					ignored_items = []
					ignored = False
				time.sleep(5)

			else:
				items_price = 0
				for i in range(len(own_items)):
					items_price += own_items[i][1]
				
				print("Items price: {}$".format(round(items_price/100, 2)))
				cm_items_res = get_cm_items()
				cm_items = cm_items_res[0]
				bots_cm_name = cm_items_res[1]
				bots_cm_id = cm_items_res[2]

				W = int(items_price)
				print('Generated cm items list')
				best_price = -1e+10
				deal_bot = 0
				best_deal = []
				for i in range(len(cm_items)):
					result = knapsack(W-1, *[[it[j] for it in cm_items[i]] for j in [1, 2]], len(cm_items[i]))
					if result[0] > best_price:
						best_price = result[0]
						best_deal = result[1]
						deal_bot = i

				print('--------')
				print("{}% ({}$)".format(round((best_price/items_price-1)*100, 2), round((best_price-W)/100., 2)))
				print('--------')
				cookies = {'cookie': all_cookies[USER]['cm']['cookie']}
				headers = {'Accept':'*/*','Accept-Encoding':'gzip, deflate, br','Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,uk;q=0.2','Connection':'keep-alive', 'Content-Length':'118', 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','DNT':'1','Host':'cs.money','Origin':'https://cs.money','Referer':'https://cs.money/','User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36', 'X-Requested-With':'XMLHttpRequest'} 
				scraper = cfscrape.create_scraper()

				print('-------***', bots_cm_name[deal_bot], '***-------')
				bot_sum = float(sum([cm_items[deal_bot][i][1] for i in best_deal])/100)
				data = "steamid="+str(bots_info[bots_cm_name[deal_bot]])+"&botItems="+json.dumps([str(cm_items[deal_bot][i][0]) for i in best_deal])+"&peopleItems="+json.dumps([own_items[i][2] for i in range(len(own_items))])+'&userSum='+str(sum([float(own_items[i][1]/100.) for i in range(len(own_items))]))+'&botSum='+str(bot_sum)
				r = scraper.post('https://cs.money/send_offer', data = data, cookies = cookies, headers = headers)
				if r.text == 'OK':
					with open('tradelist_'+USER+'.json', 'r', encoding="utf8") as fa:
						try:
							tradelist = json.load(fa)
						except EOFError:
							tradelist = {}
						except BaseException as e:
							print("#2", e)

						for item in [cm_items[deal_bot][i] for i in best_deal]:
							item_name = item[3]
							print(item_name, float(item[2]), float(item[1]), float(item[2]) / float(item[1]), float(item[1]) > 400)
							if float(item[2]) / float(item[1]) < 1.04 and float(item[1]) > 400: # profit < 3% & price > 5
								if not item_name in tradelist:
									print(item_name.encode("utf-8"), " -> for_parse")
								else:
									if tradelist[item_name] == "to_emp":
										print(item_name.encode("utf-8"), " -> for_parse (was to_emp)")
								tradelist[item_name] = 'for_parse'
							else:
								if not item_name in tradelist:
									print(item_name.encode("utf-8"), " -> to_emp")
								tradelist[item_name] = 'to_emp'
						try:
							with open('tradelist_'+USER+'.json', 'w') as fw:
								json.dump(tradelist, fw)
						except BaseException as e:
							print("#3", e)
					print('added to tradelist_'+USER+'.json')

					ignored_items = [str(own_items[i][2]) for i in range(len(own_items))]
					ignored = False
				else:
					print(r.text)
					ignored_items = []
					ignored = False
					time.sleep(5)
		time.sleep(10)

	if __name__ == "__main__":
		while True:
			try:
				main()
			except SystemExit as e:
				if str(e) == "ok":
					break
			except BaseException as e:
				print(e)
			except:
				print("unknown error")
except:
	print('Got exception\n\n')
	raise