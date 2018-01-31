function startCountdown(sum, start) {
    delay = start - (new Date());

    var socket = io.connect(rouletteServerAddress, {
        path: rouletteServerPath,
        transports: ["websocket"],
        reconnectionDelay: 5e3,
        reconnectionAttempts: 1
    });

    zero = Math.ceil(sum/.15)/100;
    colour = Math.ceil((sum-zero)*100)/100;

    function bet() {
        socket.on("roll", bet_it);
    }

    function bet_it(e) {
        setTimeout(function() {
            betsVue.amountToBet = colour;
            betsVue.placeBet("ct");
            betsVue.amountToBet = zero;
            betsVue.placeBet("bonus");
            socket.removeListener("roll", bet_it);
            socket = null;
            zero = 0;
            colour = 0;
        }, 12250 + Math.random() * 150)
    }

    setTimeout(bet, delay);
}