import random
import cfscrape
import pickle
import requests
import json
import time
import os
import sys
from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions, steam_id_to_account_id
import hustle
import logging
from hacks import log as print

tries = 0

try:

	logging.basicConfig(format='%(asctime)s | %(message)s', datefmt='%d.%m.%Y %H:%M:%S', filemode='w', filename=sys.argv[1])

	with open('cookies.json', 'r') as f:
		all_cookies = json.load(f)

	if len(sys.argv) > 2:
		cause = sys.argv[2]
		emp_cook1 = {'__cfduid': all_cookies['user1']['emp']['__cfduid'], 'PHPSESSID': all_cookies['user1']['emp']['PHPSESSID']}
		emp_s1 = requests.Session()
		emp_s1.cookies.update(emp_cook1)

		emp_cook2 = {'__cfduid': all_cookies['user2']['emp']['__cfduid'], 'PHPSESSID': all_cookies['user2']['emp']['PHPSESSID']}
		emp_s2 = requests.Session()
		emp_s2.cookies.update(emp_cook2)
	else:
		cause = "pre-divide"

	print("Dividing cause:", cause)

	user_1_api_key = all_cookies['user1']['api']
	user_1_login = all_cookies['user1']['username']
	user_1_pass = all_cookies['user1']['password']
	user_1_mafile = all_cookies['user1']['sgpath']

	user_2_api_key = all_cookies['user2']['api']
	user_2_login = all_cookies['user2']['username']
	user_2_pass = all_cookies['user2']['password']
	user_2_mafile = all_cookies['user2']['sgpath']

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

	#Stason
	cookies1 = {'Cookie':'__cfduid='+cfduid1+';steamid='+steamid1+';new_1_csrf='+new_1_csrf1}
	trade_url1 = all_cookies['user1']['emp']['trade_url']
	#user_2nator
	cookies2 = {'Cookie':'__cfduid='+cfduid2+';steamid='+steamid2+';new_1_csrf='+new_1_csrf2}
	trade_url2 = all_cookies['user2']['emp']['trade_url']
	# wrote_info = False

	with open('user1.pickle', 'rb') as f:
		client1 = pickle.load(f)
	with open('user2.pickle', 'rb') as f:
		client2 = pickle.load(f)

	if not client1.is_session_alive():
		client1 = SteamClient(user_1_api_key)
		attemts = 0
		print('Trying to login Staison')
		while (1):
			if attemts == 3:
				hustle.write("Перезагрузи роутер, дядя. (too many try_logins on divider user1)", "house_trader")
				time.sleep(40)
			try:
				print('Try login user1')
				client1.login(user_1_login, user_1_pass, user_1_mafile)
			except Exception as e:
				attemts += 1
				print(e)
				time.sleep(10)
				continue
			else:
				break
		print('Staison was logged in successfully by API')
		with open('user1.pickle', 'wb') as f:
			pickle.dump(client1, f)
	else:
		print('Staison was logged in successfully by pickle')

	if not client2.is_session_alive():
		client2 = SteamClient(user_2_api_key)
		attemts = 0
		print('Trying to login Leha')
		while (1):
			if attemts == 3:
				hustle.write("Перезагрузи роутер, дядя. (too many try_logins on divider user2)", "house_trader")
				time.sleep(40)
			try:
				print('Try login user2')
				client2.login(user_2_login, user_2_pass, user_2_mafile)
			except Exception as e:
				attemts += 1
				print(e)
				time.sleep(10)
				continue
			else:
				break
		print('Leha was logged in successfully by API')
		with open('user2.pickle', 'wb') as f:
			pickle.dump(client2, f)
	else:
		print('Leha was logged in successfully by pickle')

	def main():
		global client1, client2
		# global wrote_info
		global tries
		old_user1 = []
		old_user2 = []
		user1 = []
		user2 = []
		arr = []
		sum1 = 0
		sum2 = 0
		min_element = 10000000

		while True:
			try:
				with open('tradelist.json', 'r', encoding='utf8') as fa:
					table = json.load(fa)
				break
			except BaseException as e:
				print(e)
			except:
				print("unknown error")

		if cause == "empauto":
			print("Getting user_1 inventory")
			while True:
				try:
					sum1 = 0
					emp_req1 = emp_s1.get('https://csgoempire.com/api/get_user_items', headers=hdrs)
					emp_prices1 = emp_req1.content.decode("utf-8")
					emp_prs1 =  json.loads(emp_prices1)
					if 'error' in emp_prs1:
						if emp_prs1['error'] == 'You have no items in your inventory.':
							break
					else:
						emp_prs1 = emp_prs1['data']
					for al in emp_prs1:
						if int(al['market_value']) > 0 and (al['market_name'].find("Case Key")==-1 or al['market_name']=="CS:GO Case Key"):
							if al['market_name'] in table:
								if table[al['market_name']] == "to_emp":
									old_user1.append([int(al['market_value']), al['asset_id']])
									sum1 += int(al['market_value'])
									if int(al['market_value']) < min_element:
										min_element = int(al['market_value'])
					break
				except BaseException as e:
					print(e)

			print("Getting user_2 inventory")
			while True:
				try:
					sum2 = 0
					print(1)
					emp_req2 = emp_s2.get('https://csgoempire.com/api/get_user_items', headers=hdrs)
					emp_prices2 = emp_req2.content.decode("utf-8")
					emp_prs2 =  json.loads(emp_prices2)
					if 'error' in emp_prs2:
						if emp_prs2['error'] == 'You have no items in your inventory.':
							break
					else:
						emp_prs2 = emp_prs2['data']
					for al in emp_prs2:
						if int(al['market_value']) > 0 and (al['market_name'].find("Case Key")==-1 or al['market_name']=="CS:GO Case Key"):
							if al['market_name'] in table:
								if table[al['market_name']] == "to_emp":
									old_user2.append([int(al['market_value']), al['asset_id']])
									sum2 += int(al['market_value'])
									if int(al['market_value']) < min_element:
										min_element = int(al['market_value'])
					break
				except BaseException as e:
					print(e)
		else:
			print("Getting user_1 inventory")
			while(1):
				try:
					scraper = cfscrape.create_scraper()
					sp1 = scraper.get('https://cs.money/load_inventory?hash='+str(int(time.time()*1000)), headers=hdrs, cookies=cookies1)
					mark1 = sp1.content
					prices1 = mark1.decode("utf-8")
					prs1 = json.loads(prices1)
					sum1 = 0
					for i in prs1:
						if i['m'] in table:
							if table[i['m']] == "for_parse":
								if i['t'] != 'ky' and i.get('a') != 'only_give':
									# if cause == "empauto":
									# 	if i['m'] in user1_skins:
									# 		user1_skins[i['m']].append(i["id"])
									# 	else:
									# 		user1_skins[i['m']] = [i["id"]]
									# else:
									pr = int(round(float(i['p']*(i['r']+2)/100),2)*100)
									old_user1.append([pr, i["id"]])
									sum1 += pr
									if pr < min_element:
										min_element = pr
					break
				except:
					print("Couldn't get Staison's inventory. Gonna try again.")
					time.sleep(3)

			print("Getting user_2 inventory")
			while(1):
				try:
					scraper = cfscrape.create_scraper()
					sp2 = scraper.get('https://cs.money/load_inventory?hash='+str(int(time.time()*1000)), headers=hdrs, cookies=cookies2)
					mark2 = sp2.content
					prices2 = mark2.decode("utf-8")
					prs2 = json.loads(prices2)
					sum2 = 0
					for i in prs2:
						if i['m'] in table:
							if table[i['m']] == "for_parse":
								if i['t'] != 'ky' and i.get('a') != 'only_give':
									# if cause == "empauto":
									# 	if i['m'] in user2_skins:
									# 		user2_skins[i['m']].append(i["id"])
									# 	else:
									# 		user2_skins[i['m']] = [i["id"]]
									# else:
									pr = int(round(float(i.get('p')*(i.get('r')+2)/100),2)*100)
									old_user2.append([pr, i.get("id")])
									sum2 += pr
									if pr < min_element:
										min_element = pr
					break
				except:
					print("Couldn't get Leha's inventory. Gonna try again.")
					time.sleep(3)

		print(cause)
		print("User1 shmot: ", old_user1)
		print("User2 shmot: ", old_user2)
		print("Due to {}: Staison inventory: ${}, Leha inventory ${}".format(('empire' if cause == 'empauto' else 'cs.money'), sum1/100.,sum2/100.))
		print("Min shmot ${}".format(min_element/100.))
		# if not wrote_info:
		# 	#hustle.write("По цінах {} у Staison ${}, у Leha inventory ${}".format(('empire' if cause == 'empauto' else 'cs.money'), sum1/100.,sum2/100.), "house_trader")
		# 	wrote_info = True

		if abs(sum1 - sum2) > min_element and min(sum1, sum2)/float(sum1 + sum2) < 0.48:

			sum11=0
			sum22=0
			arr.extend(old_user1)
			arr.extend(old_user2)
			arr.sort(key=lambda x: x[0], reverse = True)

			for n in range(len(arr)):
				if sum11 < sum22:
					user1.append(arr[n])
					sum11 += arr[n][0]
				else:
					user2.append(arr[n])
					sum22 += arr[n][0]

			print("After dividing: Staison ${}, Leha ${}".format(sum11/100., sum22/100.))

			trade1 = []
			trade2 = []
			#trade1_test = []
			#trade2_test = []
			game = GameOptions.CS
			for i in range(len(user1)):
				if user1[i] not in old_user1:
					trade1.append(Asset(user1[i][1],game))
					#trade1_test.append(i[0])
			print("Asset1 generated")
			for i in range(len(user2)):
				if user2[i] not in old_user2:
					trade2.append(Asset(user2[i][1],game))
					#trade2_test.append(i[0])
			print("Asset2 generated")

			print("start making offer")

			#print(trade1_test, '\n', trade2_test)

			send_offer_errors = 0
			while True:
				try:
					trade_id = 0
					try:
						trade_id = client1.make_offer(trade2, trade1, steamid2)
						if isinstance(trade_id, dict):
							if 'strError' in trade_id:
								send_offer_errors += 1
								if send_offer_errors >=4:
									time.sleep(30)
									raise SystemExit("redivide")
								if trade_id['strError'] == 'There was an error sending your trade offer.  Please try again later. (26)':
									print("error sending trade offer, gonna sleep")
									time.sleep(30)
									continue
						print("made offer:", trade_id)
					except BaseException as e:
						print("#0", e, "; for trade_id:",trade_id)

					if trade_id == 0:
						print("getting offer id error, trying to list all offers")
						for i in range(5):
							try:
								offers = client2.get_trade_offers()['response']['trade_offers_received']
								for offer in offers:
									if int(offer['accountid_other']) == int(steam_id_to_account_id(all_cookies['user1']['steamid'])):
										print("found", offer['tradeofferid'])
										trade_id = offer['tradeofferid']
										raise SystemExit("break loop")
								time.sleep(10)
							except SystemExit as e:
								if str(e) == "break loop":
									break
							except:
								print("unknown error")
						if trade_id == 0:
							print("repeat")
							continue

					# offer = client1.get_trade_offer(trade_id)['response']['offer']
					# accept_tries = 0
					# while offer['trade_offer_state'] != 3:
					# 	accept_tries += 1
					# 	try:
					# 		client1.accept_trade_offer(trade_id)
					# 		client2.accept_trade_offer(trade_id)
					# 	except BaseException as e:
					# 		print("#1:", e)
					# 		if accept_tries >= 10:
					# 			accept_tries = 0
					# 			break
					# 	finally:
					# 		time.sleep(5)

					# if accept_tries == 0:
					# 	continue
					for i in range(10):
						try:
							offer = client1.get_trade_offer(trade_id)['response']['offer']
						except BaseException as e:
							print("#2:",e)
							if str(e) == "'descriptions'":
								hustle.write("Знач, поділили так: Staison ${}, Leha ${}".format(sum11/100., sum22/100.), "house_trader")
								raise SystemExit("ok")
						except:
							raise SystemExit("redivide")
						time.sleep(6)

					break
				except SystemExit as e:
					print("#3:",e)
					if str(e) == "ok" or str(e) == "redivide":
						raise
				except BaseException as e:
					print(e)
				except:
					print("unknown error")

			# if offer['trade_offer_state'] == 3:
			# 	hustle.write("Знач, поділили так: Staison ${}, Leha ${}".format(sum11/100., sum22/100.), "house_trader") # Accepted
			# else:
			# 	raise SystemExit("redivide")
			
			# hustle.write("After dividing: Staison ${}, Leha ${}".format(sum11/100., sum22/100.), "house_trader")
		else:
			# if tries > 0:
			# 	hustle.write("After dividing: Staison ${}, Leha ${}".format(sum1/100., sum2/100.), "house_trader")
			# 	print("Divided.")
			# else:
			if cause == "empauto":
				hustle.write("Ну тут все ровненько більш-менш (у Стаса {}$ по версії empire, у Льохи {}$), мінять не буду, ща заллю по фасту.".format(round(sum1/100., 2), round(sum2/100., 2)), "house_trader")
			else:
				hustle.write("Та безсмисленно мінять шось, парсю.", "house_trader")
			print("No reason to divide inventories.")
			raise SystemExit("ok")

	if __name__ == '__main__':
		while True:
			try:
				main()
			except SystemExit as e:
				if str(e) == "ok":
					break
				elif str(e) == "redivide":
					print("Dividing error. Try again.")
			except BaseException as e:
				print(e)
			except:
				print("unknown error")
except:
	print('Got exception\n\n')
	raise