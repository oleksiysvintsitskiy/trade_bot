import requests
import json
import time
import sys
import pickle
import cfscrape
from steampy.client import SteamClient, Asset, TradeOfferState
from steampy.utils import GameOptions,steam_id_to_account_id
import logging
from hacks import log as print

proxy = -1

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
    }
]

logging.basicConfig(format='%(asctime)s | %(message)s', datefmt='%d.%m.%Y %H:%M:%S', filemode='w', filename=sys.argv[2])

hdrs = {'User-Agent': 'Mozilla / 537.36 (KHTML, like Gecko) Chrome /'}

USER = sys.argv[1]
with open('cookies.json', 'r') as f:
    all_cookies = json.load(f)

my_cookie = {'__cfduid': all_cookies[USER]['emp']['__cfduid'], 'PHPSESSID': all_cookies[USER]['emp']['PHPSESSID']}
data = all_cookies[USER]['tradelink']

with open(USER+'.pickle', 'rb') as f:
    client = pickle.load(f)

print("Loaded pickle file.")

if not client.is_session_alive():
    client = SteamClient(all_cookies[USER]['api'])
    while True:
        try:
            print('Try login '+USER)
            if client.login(all_cookies[USER]['username'], all_cookies[USER]['password'], all_cookies[USER]['sgpath']) != None:
                break
        except Exception as e:
            if str(e).find('There have been too many login failures from your network in a short time period') != -1:
                proxy += 1
                if proxy >= len(proxies):
                    proxy = 0
                client._session.proxies.update(proxies[proxy])
                print("Trying with proxy", proxies[proxy]['http'])
            else:
                print("#0:",e)
                time.sleep(10)
            continue
        else:
            break
    print(('Staison' if USER == 'user1' else 'Leha')+' was logged in successfully by API')
    with open(USER+'.pickle', 'wb') as f:
        pickle.dump(client, f)
else:
    print(('Staison' if USER == 'user1' else 'Leha')+' was logged in successfully by pickle')

# Set API key
api_key = all_cookies[USER]['api']
# Set path to SteamGuard file
steamguard_path = all_cookies[USER]['sgpath']
# Steam username
username = all_cookies[USER]['username']
# Steam password
password = all_cookies[USER]['password']

def decline_all_trade(client):
    try:
        print('Start decline all offers')
        offers = []
        now = int(time.time())
        while ((int(int(time.time()) - int(now)) < int(30)) and (int(len(offers)) == int(0))):
            time.sleep(2)
            offers = client.get_trade_offers()['response']['trade_offers_received']
        for offer in offers:
            client.decline_trade_offer(offer['tradeofferid'])
            print('Decline offer')
    except:
            print('Error when decline')
    else:
        return

def get_own_items_from_emp(output, s, table):
    cheker = 0
    while True:
        try:
            sp = s.get('https://csgoempire.com/api/get_user_items', headers=hdrs)
            mark = sp.content
            prices = mark.decode("utf-8")

            temp =  json.loads(prices)

            if temp['success'] == False:
                if temp['error'] == 'No valid items found. Only items worth at least $0.50 are accepted.' or temp['error'] == 'You have no items in your inventory.':
                    raise SystemExit("no items")
                else:
                    cheker += 1
                    if cheker==10:
                        sys.exit(3)
                    time.sleep(1)
                    continue
            else:
                prs = temp.get('data')
                break
        except BaseException as e:
            if str(e) == "no items":
                raise SystemExit("no items")
            print("get user items error:",e)
    while True:
        try:
            for al in prs:
                if al['market_value'] > 0 and (al['market_name'].find("Case Key")==-1 or al['market_name']=="CS:GO Case Key"):
                    if al['market_name'] in table:
                        if table[al['market_name']] == "to_emp":
                            output.append([al['asset_id'], al['market_value']])
            break
        except BaseException as e:
            print("making items array error:",e)
    return

def main():
    with open('tradelist.json', 'r', encoding='utf8') as fa:
        try:
            table = json.load(fa)
        except EOFError:
            table = {}
    s = requests.Session()
    s.cookies.update(my_cookie)
    it = []
    get_own_items_from_emp(it, s, table)
    print(len(it))
    if len(it)==0:
        raise SystemExit("no items")
    timeOff = 0
    while (len(it) != 0):
        it=[]
        get_own_items_from_emp(it, s, table)
        print(len(it))
        if len(it) == 0:
            raise SystemExit("no items")
        i = 0
        offerItem = []
        while(len(offerItem)!=8):
            offerItem.append(it[i][0])
            i += 1
            if i==len(it):
                break
        if (1):
            if (len(it)) % 8 != 0:
                print('Left offers:' + str(int((len(it)) / 8) + 1))
            else:
                print('Left offers:' + str(int((len(it)) / 8)))
            hd = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br',
                  'accept-language': 'en-US,en;q=0.8,ru;q=0.6,uk;q=0.4',
                  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                  'x-requested-with': 'XMLHttpRequest'}
            setOffer = s.post('https://csgoempire.com/api/set_trade_url', data=data, headers=hd)

            print("set_offer content:",setOffer.content)
            dat = 'transfer_type=deposit'
            for item in offerItem:
                dat = dat + '&asset_ids%5B%5D=' + str(item)
            offerItem = []
            timeNow = int(time.time())
            itera = 0
            while (True):
                if itera >= 15:
                    sys.exit(5)
                print('Try send')
                sendtrade = s.post('https://csgoempire.com/api/transfer_items', data=dat, headers=hd)
                temp = json.loads(((sendtrade.content).decode("utf-8")))
                print(temp)
                if temp['data']['status']=='processing':
                    itera+=1
                if (str(temp['success']) == 'False') or (str(temp['success']) == 'false'):
                    if (str(temp['error']) == 'Invalid request'):
                        sys.exit(5)

                    if (int(time.time()) - timeNow) > int(15):
                        decline_all_trade(client)

                    else:
                        time.sleep(2)
                else:
                    code = json.loads(((sendtrade.content).decode("utf-8")))['data']['code']
                    raise SystemExit("restart script")
                time.sleep(3)
                continue
            url = 'https://csgoempire.com/api/check_transfer?transfer_type=deposit&code=' + str(code)
            dt = 'transfer_type=deposit&code=' + str(code)
            offer_id = ''

            while True:
                try:
                    fgh = 0
                    print('Try check')
                    while (offer_id == ''):
                        checkoffer = s.post(url, data=dt, headers=hd)
                        print("check offer content:", checkoffer.content)
                        parsed = json.loads((checkoffer.content).decode("utf-8"))
                        if parsed['success'] == False:
                            fgh = 1
                            break
                        if parsed['data']['status'] == 'sent':
                            offer_id = parsed['data']['offer_id']
                        time.sleep(2)
                except:
                    time.sleep(2)
                    continue
                else:
                    break
            if fgh == 1:
                continue
            try:
                print('Start accept_trade_offer')
                check = 0
                while True:
                    try:
                        print('Try accept')
                        offr = client.get_trade_offer(offer_id)['response']['offer']
                        print('Trade offer state: ' + str(offr['trade_offer_state']))
                        while (offr['trade_offer_state'] == TradeOfferState.Active):
                            print('Try one more time')
                            client.accept_trade_offer(offer_id)
                            print('Done')
                            break
                    except:
                        check = check + 1
                        try:
                            offr = client.get_trade_offer(offer_id)['response']['offer']
                        except:
                            print('Can\'t update offer')
                        time.sleep(2)
                        if check == int(10):
                            print('Are you ahueli tam?')
                            # 'Restart me')
                            sys.exit(3)
                    else:
                        time.sleep(10)
                        break
            except:
                print('Error, skip this trade')

if __name__ == '__main__':
    while True:
        try:
            main()
        except SystemExit as e:
            if str(e) == "no items":
                print(e)
                break
            if str(e) == "restart script":
                pass
            print("#1:", e)
        except BaseException as e:
            print("#2:",e)
        except:
            print("unknown error")