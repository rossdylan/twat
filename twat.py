import eventlet
eventlet.monkey_patch()
import json
from eventlet import wsgi, websocket
from time import sleep
import requests
from threading import Thread
def getHashTags(tweet):
    """Filter out all the hashtags within a tweet
    :param tweet: tweet to filter
    :type tweet: str
    """
    hashTags = []
    sections = tweet.split(" ")
    for section in sections:
        if section.startswith("#"):
            subsections = section.split("#")
            for subsection in subsections:
                if subsection != "":
                    try:
                        tag = subsection.decode('utf-8').strip().lower()
                        if not tag in hashTags:
                            hashTags.append(tag)
                    except:
                        pass
    return hashTags

def streamData(response,hashCounts):
    """Run in a thread to stream data from twitter and store it
    :param response: response object from requests.get
    :param hashCounts: Dict in a Dict to store the data received from twitter
    :type hashCounts: dict
    """
    try:
        for line in r.iter_lines():
            if line:
                twitterStuff = json.loads(line)
                if not 'delete' in twitterStuff and twitterStuff['geo'] != None:
                    text = twitterStuff['text']
                    hashTags = getHashTags(text)
                    loc = str(twitterStuff['geo']['coordinates'])

                    if hashTags != []:
                        if not loc in hashCounts:
                            hashCounts[loc] = {}
                        for tag in hashTags:
                            if tag in hashCounts[loc]:
                                hashCounts[loc][tag] += 1
                            else:
                                hashCounts[loc][tag] = 1
    except KeyboardInterrupt:
        print "error"
        exit(1)
def toGeoJson(d):
    geojsonblobs = []
    for location in d:
        location = location.split(", ")
        location = (float(location[0][1:]), float(location[1][:-1]))
        geojsonblobs.append({"type": "Point", "coordinates": location})
    return geojsonblobs

if __name__ == "__main__":
    hashCounts = {}
    global clients
    clients = 0

    @websocket.WebSocketWSGI
    def hashtag_callback(ws):
        """
        :param ws: pass a websocket connect to the handler
        :type ws: WebSocket
        """
        global clients
        last = {}
        clients += 1
        print "Clients:", clients
        data = ws.wait()
        print data
        if data == "ready":
            while True:
                sleep(2)
                if last == hashCounts:
                    continue
                else:
                    ws.send(json.dumps(toGeoJson(hashCounts)))
                    last = hashCounts
        clients -= 1
        print "Disconnecting"

    def dispatch(environ,start_response):
        """
        :param environ: wsgi environment variables
        :param start_response: wsgi response thingy?
        """
        if environ['PATH_INFO'] == '/tweets':
            if environ['HTTP_UPGRADE'] == 'websocket':
                environ['HTTP_UPGRADE'] = 'WebSocket'
            return hashtag_callback(environ,start_response)
        elif environ['PATH_INFO'] == '/ws.js':
            start_response('200', [('Content-Type', 'text/javascript')])
            return [open("ws.js").read()]
        elif environ['PATH_INFO'] == '/ws.html':
            start_response('200', [('Content-Type', 'text/html')])
            return [open("ws.html").read()]
        elif environ['PATH_INFO'] == "/polymaps.min.js":
            start_response('200', [('Content-Type', 'text/javascript')])
            return [open("polymaps.min.js").read()]
        else:
            start_response("404", [])
            return []
    r = requests.get('https://stream.twitter.com/1/statuses/sample.json',
            data={'track': 'requests'}, auth=(raw_input("username: "), raw_input("password: ")))

    t = Thread(target=streamData,args=(r,hashCounts))
    t.start()
    wsgi.server(eventlet.listen(('0.0.0.0',8090)), dispatch)

