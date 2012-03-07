window.onload = function() {
	console.log("Starting ws shits");
	var ws = new WebSocket("ws://carthage.csh.rit.edu:8090/tweets");
	ws.onerror = function(e) { console.log(e); }
	ws.onopen = function() { console.log("onopen"); ws.send("ready"); }
	ws.onmessage = function(e) {console.log(e.data);}
	ws.onclose = function() { console.log("onclose"); }
};
