#!/usr/bin/python
import websocket
import threading
import time


def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    print 'ws opened'


class WebSocketClient(threading.Thread):
    def __init__(self, url):
        super(WebSocketClient, self).__init__()
        headers = {
            'Cookie':
                      'z_c0="QUFEQS1NY1pBQUFYQUFBQVlRSlZUVmpkTGxmbVplRUNmMlhEZHpFV0VqMlpEdDEwUGVZYktRPT0=|1460097111|5b7864d77f8826b9f8056e08131be186e1c7486e"; '
                      ,
            'Accept-Language': 'en-US,en;q=0.8', 'Pragma': 'no-cache',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'}
        self.header_list = []
        self.url = url
        # self.cookie_dic =
        for key, value in headers.iteritems():
            self.header_list.append(key+':'+value)

    def run(self):


        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    on_open=on_open,
                                    # cookie=cookie_dic,
                                    header=self.header_list
                                    )
        print 'ff'
        ws.run_forever(host='comet.zhihu.com', origin='https://www.zhihu.com')
        print 'dd'


if __name__ == '__main__':
    a = WebSocketClient(url='wss://comet.zhihu.com/apilive')
    a.start()