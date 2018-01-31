import json
import pickle
import paramiko
import requests
import cfscrape
import itertools
import time
import sys
import telebot
import hustle
from steampy.client import SteamClient, TradeOfferState, Asset
from steampy.utils import GameOptions, steam_id_to_account_id

proxy = -1
proxy_counter = 0
proxies = [
	{
		'http': 'http://stanislavsidletsky:gdsfhdj34563@193.169.87.238:65233',
		'https': 'https://stanislavsidletsky:gdsfhdj34563@193.169.87.238:65233'
	},
	{
		'http': 'http://stanislavsidletsky:gdsfhdj34563@91.217.90.157:65233',
		'https': 'https://stanislavsidletsky:gdsfhdj34563@91.217.90.157:65233'
	},
	{
		'http': 'http://stanislavsidletsky:gdsfhdj34563@176.103.48.121:65233',
		'https': 'https://stanislavsidletsky:gdsfhdj34563@176.103.48.121:65233'
	},
	{
		'http': 'http://stanislavsidletsky:gdsfhdj34563@193.169.86.207:65233',
		'https': 'https://stanislavsidletsky:gdsfhdj34563@193.169.86.207:65233'
	},
	{
		'http': 'http://stanislavsidletsky:gdsfhdj34563@91.217.90.144:65233',
		'https': 'https://stanislavsidletsky:gdsfhdj34563@91.217.90.144:65233'
	},
	{
		'http': 'http://stanislavsidletsky:gdsfhdj34563@176.103.49.86:65233',
		'https': 'https://stanislavsidletsky:gdsfhdj34563@176.103.49.86:65233'
	}
]

hdrs = {'User-Agent': 'Mozilla / 537.36 (KHTML, like Gecko) Chrome /'}

def main():
	global proxy, proxy_counter
	with open('cookies.json', 'r') as f:
		all_cookies = json.load(f)

	USER = sys.argv[1]

	client = 0

	with open(USER+'.pickle', 'rb') as f:
		client = pickle.load(f)
	
	print("Loaded pickle file.")

	if not client.is_session_alive():
		client = SteamClient(all_cookies[USER]["api"])
		while (1):
			try:
				print('Try login '+USER)
				if client.login(all_cookies[USER]["username"], all_cookies[USER]["password"], all_cookies[USER]["sgpath"]) != None:
					break
			except Exception as e:
				print(e)
				if str(e).find('There have been too many login failures from your network in a short time period') != -1:
					if proxy_counter >= 10:
						hustle.write("Proxy " + USER, "house_trader")
						raise BaseException("reload")
					proxy += 1
					if proxy >= len(proxies):
						proxy = 0
					client._session.proxies.update(proxies[proxy])
					print("Trying with proxy", proxies[proxy]['http'])
					proxy_counter += 1
				continue
			else:
				break
		print(('Staison' if USER == 'user1' else 'Leha')+' was logged in successfully by API')
		with open(USER+'.pickle', 'wb') as f:
			pickle.dump(client, f)
	else:
		print(('Staison' if USER == 'user1' else 'Leha')+' was logged in successfully by pickle')
	
	fails = 0
	while True:
		offers=[]
		try:
			offers = client.get_trade_offers()['response']['trade_offers_received']
			time.sleep(3)
			print('Found ' + str(len(offers)) + ' offers')
		except:
			print('Can\'t get offer. Steam lags?')

		while len(offers) > 0:
			print('Found ' + str(len(offers)) + ' offers')
			for offer in offers:
				try:
					offer = client.get_trade_offer(offer['tradeofferid'])['response']['offer']
					#print('Trade offer state: ' + str(offer['trade_offer_state']))
					#print(offer['trade_offer_state'])
					if offer['trade_offer_state'] == TradeOfferState.Active:
						#print(offer['tradeofferid'])
						print(offer['tradeofferid'], client.accept_trade_offer(offer['tradeofferid']))
						#print("trying accept")
						#print(offer['tradeofferid'], 'accepted')
						continue
					#if offer['trade_offer_state'] == TradeOfferState.Accepted:
						
				except BaseException as e:
					fails += 1
					if fails >= 13:
						fails = 0
						print("Probaly session error. Relogin.")
						client = SteamClient(all_cookies[USER]["api"])
						while (1):
							try:
								print('Try login '+USER)
								if client.login(all_cookies[USER]["username"], all_cookies[USER]["password"], all_cookies[USER]["sgpath"]) != None:
									break
							except Exception as e:
								if str(e).find('There have been too many login failures from your network in a short time period') != -1:
									if proxy_counter >= 10:
										hustle.write("Proxy " + USER, "house_trader")
										raise BaseException("reload")
									proxy += 1
									if proxy >= len(proxies):
										proxy = 0
									client._session.proxies.update(proxies[proxy])
									print("Trying with proxy", proxies[proxy]['http'])
									proxy_counter += 1
								# if str(e) == 'There have been too many login failures from your network in a short time period.  Please wait and try again later.':
								# 	time.sleep(30)
								# 	raise Exception("reload")
								continue
							else:
								break
						print(('Staison' if USER == 'user1' else 'Leha')+' was logged in successfully by API')
						with open(USER+'.pickle', 'wb') as f:
							pickle.dump(client, f)
					print(e)
				# except:
				# 	raise
			offers = client.get_trade_offers()['response']['trade_offers_received']
			time.sleep(3)

if __name__ == '__main__':
	counter = 0
	while True:
		if counter >=6:
			hustle.write("Дядя, ну проксі не спасає, гаси сізіфа!", "house_trader")
			time.sleep(900)
		try:
			main()
			break
		except Exception as e:
			print(e)
			if str(e) == "reload":
				counter += 1	
		except BaseException as e:
			print(e)
			if str(e) == "reload":
				counter += 1