import json
import sys


with open('tradelist_user1.json', 'r', encoding='utf8') as fa:
	table1 = json.load(fa)
with open('tradelist_user2.json', 'r', encoding='utf8') as fa:
	table2 = json.load(fa)

table3 = {}

for i in table1:
	table3[i] = table1[i]
for i in table2:
	table3[i] = table2[i]

with open('tradelist.json', 'w', encoding='utf8') as fw:
	json.dump(table3, fw)
