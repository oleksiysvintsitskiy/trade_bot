var io = require('socket.io-client'),
fs = require('fs'),
request = require('request');

sockets = [];

function roll_socket(token) {
	this.bet = function(zero, colour, coin) {
		console.log(zero, colour, coin)
		this.socket.emit('place bet', {
			round: this.roundID,
			coin: coin,
			amount: colour
		});
		this.socket.emit('place bet', {
			round: this.roundID,
			coin: "bonus",
			amount: zero
		});
	}
	this.roundID = 0;
	this.can_bet = false;
	this.rolled = false;
	this.can_change_rolled = false;
	this.update_time = 0;
	this.socket_token = token;
	this.socket = io.connect('csgoempire.com', {
		port: 443,
		path: "/ws/socketio/",
		transports: ['websocket']
	});
	this.socket.on('connect', () => {
		console.log("socket connected");
		this.update_time = +new Date();
	});
	this.socket.on('connect_error', (e) => {
		console.log(e);
	});
	this.socket.emit('identify', {token: this.socket_token});
	this.socket.on('init', (res) => {
		this.roundID = res.round;
		this.update_time = +new Date();
	});
	this.socket.on('bet', (res) => {
		this.can_bet = true;
		this.update_time = +new Date();
	});
	this.socket.on('roll', (res) => {
		if(this.can_change_rolled) {
			this.rolled = true;
		}
		this.can_bet = false;
		this.roundID = res.new_round;
		this.update_time = +new Date();
	});
}

fs.readFile('../cookies.json', (err, data) => {
	all_cookies = JSON.parse(data);
	for(var USER in all_cookies) {
		request({
			method: "GET",
			url: "https://csgoempire.com/api/get_socket_token",
			headers: {
				"accept": "*/*",
				//"accept-encoding": "gzip, deflate, sdch, br",
				"accept-language": "ru,uk;q=0.8,en;q=0.6,de;q=0.4",
				"referer": "https://csgoempire.com/",
				"cookie": "__cfduid="+all_cookies[USER]["emp"]["__cfduid"]+"; PHPSESSID="+all_cookies[USER]["emp"]["PHPSESSID"],
				"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
				"x-requested-with": "XMLHttpRequest"
			}
		}, function(error, response, data) {
			sockets.push(new roll_socket(JSON.parse(data).data.socket_token));
		});
	}
});


function roll_checker() {
	fs.readFile('../logs/withdraw.json', (err, data) => {
		data = JSON.parse(data);
		if(data["user1"] > 0 && data["user2"] > 0) {
			sockets[0].can_change_rolled = true;
			sockets[1].can_change_rolled = true;
			max_bet = Math.max(data["user1"], data["user2"]);
			console.log("must bet " + max_bet + "$");
			clearInterval(file_interval);
			roll_interval = setInterval(function() {
				if(Math.abs(sockets[0].update_time - sockets[1].update_time) < 1000 && sockets[0].roundID == sockets[1].roundID && sockets[0].can_bet && sockets[1].can_bet && sockets[0].rolled && sockets[1].rolled) {
					clearInterval(roll_interval);
					sockets[0].can_change_rolled = false;
					sockets[1].can_change_rolled = false;
					setTimeout(function() {
						sockets[0].rolled = false;
						sockets[1].rolled = false;
						max_bet = (max_bet+0.01)*100;
						zero = Math.ceil(max_bet/15);
						colour = Math.ceil(max_bet-zero);
						sockets[0].bet(zero, colour, "ct");
						sockets[1].bet(zero, colour, "t");
						data["user1"] = 0;
						data["user2"] = 0;
						data["rolled"] = true;
						fs.writeFile('../logs/withdraw.json', JSON.stringify(data));
						file_interval = setInterval(roll_checker, 10000);
					}, 1500+Math.round(Math.random()*1000));
				}
			}, 100);
		}
	});
}

file_interval = setInterval(roll_checker, 10000);