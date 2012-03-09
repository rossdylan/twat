var map;
var po;
window.onload = function() {
	window.po = org.polymaps;
	window.map = window.po.map()
		.container(document.getElementById("map").appendChild(window.po.svg("svg")))
		.add(window.po.interact())
		.add(window.po.hash());

	map.add(window.po.image()
		.url(window.po.url("http://{S}tile.cloudmade.com"
			+ "/e02b837fe4ed4b929d34b13b5eec9705" // http://cloudmade.com/register
			+ "/999/256/{Z}/{X}/{Y}.png")
		.hosts(["a.", "b.", "c.", ""])));

	window.map.add(window.po.compass()
		.pan("none"));

	console.log("Starting ws shits");
	var ws = new WebSocket("ws://carthage.csh.rit.edu:8090/tweets");
	ws.onerror = function(e) { console.log(e); }
	ws.onopen = function() { 
			console.log("onopen"); 
			ws.send("ready"); }
	ws.onmessage = function(e) {
			console.log(e.data);
			len = e.data.length;
			var i = 0;
			for(i=0;i<len;i++)
			{
				window.map.add(window.po.geoJson().features(e.data[i]));
			}
	}
	ws.onclose = function() { console.log("onclose"); }
};
