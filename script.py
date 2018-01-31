import json
import sys
import re

USER = sys.argv[1]


with open('f1.txt', 'r') as myfile:
    f11=myfile.read().replace('\n', '')

f1 = json.loads(f11)

tradelist = {}

for i in f1["items"]:
	print(type(i))
	if re.search("\sKey",i['name']):
		tradelist[i["name"]] = "to_money"
	elif "price" in i:
		tradelist[i["name"]] = "for_parse"
			


with open('tradelist_'+USER+'.json', 'w') as fw:
	json.dump(tradelist, fw)