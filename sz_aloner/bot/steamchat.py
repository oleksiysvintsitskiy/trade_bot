from steampy.client import SteamClient, Asset
import pickle
import json
import time
import re

def url_community(namespace, method):
	return 'https://steamcommunity.com/{namespace}/{method}/'.format(namespace=namespace, method=method)

def url_api(namespace, method, version="1"):
	return 'https://api.steampowered.com/{namespace}/{method}/v{version}/'.format(namespace=namespace, method=method, version=version)

def send_message(USER, client, text, steamid64):

	def check_http_error(response):
		"""Checks for Steam's definition of an error.
		"""
		if response.status_code >= 300 and response.status_code <= 399 and "/login" in response.headers["location"]:
			emit('session_expired')
			return True

		if response.status_code >= 400:
			return True

		return False

	def get_chat_oauth_token(return_response=False):
		ret = ()
		resp = client._session.get("https://steamcommunity.com/chat")
		if check_http_error(resp):
			ret = ("HTTP Error", None)

		token = re.compile(r'"([0-9a-f]{32})" \);')
		matches = token.search(resp.text)
		if matches:
			ret = (None, matches.groups()[0])

		if ret is ():
			ret = ("Malformed Response", None)

		if return_response:
			if hasattr(resp, "text"):
				ret += (resp.text,)
			else:
				ret += (None,)

		return ret

	with open('../cookies.json', 'r') as f:
		all_cookies = json.load(f)

	with open('../'+USER+'.pickle', 'rb') as f:
		client = pickle.load(f)
	print(client.is_session_alive())
	if not client.is_session_alive():
		client = SteamClient(all_cookies[USER]['api'])
		client.login(all_cookies[USER]['username'], all_cookies[USER]['password'], all_cookies[USER]['sgpath'])

	err, token, resp = get_chat_oauth_token(return_response=True)
	login = client._session.post(url_api("ISteamWebUserPresenceOAuth", "Logon"), data={"ui_mode": "web", "access_token": token})
	login_data = login.json()
	umqid = login_data["umqid"]

	params = {
				"access_token": token,
				"steamid_dst": steamid64,
				"text": text,
				"type": "saytext",
				"umqid": umqid
			}


	return client.api_call('POST', 'ISteamWebUserPresenceOAuth', 'Message', 'v1', params).json()

def get_last_message(client, steamid):
	form = {"sessionid": client._get_session_id()}
	resp = client._session.post(url_community("chat", "chatlog") + str(steamid), data=form)
	if not resp.ok:
		print("Error in loading chatlog: %s", resp.status_code)
		return []
	else:
		parsed = []
		#body = resp.json()
		last = resp.json()[-1]
		'''for msg in body:
			#parsed.append(Munch({
			#	"steam_id": steam_id,
			#	"timestamp": msg["m_tsTimestamp"],
			#	"message": msg["m_strMessage"]
			#}))
			if msg["m_unAccountID"] == steamid:
				print(msg, time.time())'''
		return {'id': last["m_unAccountID"], 'text': last["m_strMessage"], 'time': last["m_tsTimestamp"]}