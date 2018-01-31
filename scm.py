import json
import sys
import re


with open('f1.txt', 'r') as myfile:
    f11=myfile.read().replace('\n', '')

f1 = json.loads(f11)

tradelist = {}

for i in f1:
	if i['t']!='ky':
		tradelist[i["m"]] = "for_parse"
	else:
		tradelist[i["m"]] = "to_money"
			


with open('tradelist.json', 'w') as fw:
	json.dump(tradelist, fw)