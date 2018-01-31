var io = require('socket.io-client'),
fs = require('fs'),
request = require('request'),
socket = io.connect('cs.money', {
	port: 443,
	path: "/socket.io/",
	sid: "yF7GySIW1-6HOYtiAdUM",
	transports: ['websocket']
});
socket.on('connect', () => {
	console.log("socket connected");
});
socket.on('disconnect', (err) => {
	console.log("disconnect:",err);
});
socket.on('connect_failed', (err) => {
	console.log("failed:",err);
});
socket.on('update_list_overstock', (data) => {
	skins = JSON.parse(data);
	fs.readFile('../logs/overstock_db.json', (err, data) => {
		old_skins = JSON.parse(data);
		for(var skin in skins) {
			old_skins[skin] = {"status": skins[skin], "time": Math.floor((+new Date())/1000)}
		}
		fs.writeFile('../logs/overstock_db.tmp.json', JSON.stringify(old_skins), function() {
			fs.rename('../logs/overstock_db.tmp.json', '../logs/overstock_db.json');
		});
	});
});