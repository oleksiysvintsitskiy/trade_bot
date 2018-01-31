var io = require('socket.io-client'),
fs = require('fs'),
request = require('request'),
sockets = [],
connections = 0,
bets_cheking = 0,
prev_bal0 = 0,
prev_bal1 = 0,
roll_process = false;

function roll_socket(token) {
	this.bet = function(zero, colour, coin) {
		console.log(zero, colour, coin);
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
	this.balance = 0;
	this.socket = io.connect('csgoempire.com', {
		port: 443,
		path: "/ws/socketio/",
		transports: ['websocket']
	});
	this.socket.on('connect', () => {
		console.log("socket connected");
		connections++;
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
	this.socket.on('balance', (res) => {
		this.balance = res.balance;
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

function doBets() {
	fs.readFile('logs/withdraw.json', (err, data) => {
		data = JSON.parse(data);
		if(data["user1"] > 0 && data["user2"] > 0) {
			sockets[0].can_change_rolled = true;
			sockets[1].can_change_rolled = true;
			max_bet = Math.max(data["user1"], data["user2"]);
			console.log("must bet " + max_bet + "$");
			// clearInterval(file_interval);
			roll_process = false;
			roll_interval = setInterval(function() {
				if(!roll_process) {
					if(Math.abs(sockets[0].update_time - sockets[1].update_time) < 100 && sockets[0].roundID == sockets[1].roundID && sockets[0].can_bet && sockets[1].can_bet && sockets[0].rolled && sockets[1].rolled) {
						roll_process = true;
						clearInterval(roll_interval);
						sockets[0].can_change_rolled = false;
						sockets[1].can_change_rolled = false;
						sockets[0].rolled = false;
						sockets[1].rolled = false;
						setTimeout(function() {
							max_bet = (max_bet+0.01)*100;
							zero = Math.ceil(max_bet/15);
							colour = Math.ceil(max_bet-zero);
							sockets[0].bet(zero, colour, "ct");
							sockets[1].bet(zero, colour, "t");
							data["user1"] = 0;
							data["user2"] = 0;
							data["rolled"] = true;
							console.log("rolled. closing after 20secs delay.")
							fs.writeFile('logs/withdraw.json', JSON.stringify(data));
							//file_interval = setInterval(roll_checker, 10000);
							setTimeout(function() {
								console.log("roulette_bot exit")
								process.exit(0);
							}, 20000);
						}, 500+Math.round(Math.random()*600));
					}
				}
			}, 100);
		} else setTimeout(doBets, 10000);
	});
}

fs.readFile('cookies.json', (err, data) => {
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
	if(connections == 2) {
		if(sockets[0].balance != 0 && sockets[1].balance != 0) {
			prev_bal0 = sockets[0].balance;
			prev_bal1 = sockets[1].balance;
			console.log("Staison's balance: "+(sockets[0].balance/100)+"$");
			console.log("Leha's balance: "+(sockets[1].balance/100)+"$");
			console.log("Making test 0.01$ bet");
			processing = false;
			sockets[0].can_change_rolled = true;
			sockets[1].can_change_rolled = true;
			testInterval = setInterval(function() {
				if(!processing) {
					if(Math.abs(sockets[0].update_time - sockets[1].update_time) < 100 && sockets[0].roundID == sockets[1].roundID && sockets[0].can_bet && sockets[1].can_bet && sockets[0].rolled && sockets[1].rolled) {
						console.log("Cached best time");
						clearInterval(testInterval);
						sockets[0].can_change_rolled = false;
						sockets[1].can_change_rolled = false;
						sockets[0].rolled = false;
						sockets[1].rolled = false;
						processing = true;
						for(var i=0; i<=1; i++) {
							sockets[i].socket.emit('place bet', {
								round: sockets[i].roundID,
								coin: "ct",
								amount: 1
							});
						}
						console.log("Made bets");
						bets_cheking = 0;
						checkInterval = setInterval(function() {
							bets_cheking++;
							console.log("Checking results: ", prev_bal0, sockets[0].balance, prev_bal1, sockets[1].balance);
							if((sockets[0].balance + 1 == prev_bal0 || sockets[0].balance == prev_bal0 + 1) && (sockets[1].balance + 1 == prev_bal1 || sockets[1].balance == prev_bal1 + 1)) {
								clearInterval(checkInterval);
								setTimeout(function() {
									console.log("Alright, gonna do main bets");
									doBets();
								}, 20000);
							} else {
								if(bets_cheking > 10) {
									clearInterval(checkInterval);
									setTimeout(roll_checker, 10000);
								}
							}
						}, 3000);
					}
				}
			}, 100);
		} else setTimeout(roll_checker, 10000);
	} else setTimeout(roll_checker, 10000);
}

roll_checker();
// file_interval = setInterval(roll_checker, 10000);