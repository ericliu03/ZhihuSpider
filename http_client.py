import requests
import time
import json
from requests.adapters import HTTPAdapter

headers = {"Accept": "*/*",
           "Accept-Encoding": "gzip,deflate",
           "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
           "Connection": "keep-alive",
           "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
           "User-Agent": "User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
           "Referer": "http://www.zhihu.com/",
           "Origin": "http://www.zhihu.com/",
           'Host': 'www.zhihu.com'
           }


class Client:
    def __init__(self, proxy=None, username=None, password=None, input_captcha=False):

        self.username = username
        self.password = password
        self.input_captcha = input_captcha

        self.session = requests.Session()
        self.session.mount('http://www.zhihu.com', HTTPAdapter(max_retries=5))
        self.session.headers.update(headers)
        if proxy:
            print 'Using proxy: ' + proxy
            self.session.proxies.update({'http': proxy})

    def get_captcha(self):
        """Download captcha to a image"""
        print 'Getting captcha...'
        captcha_url = 'http://www.zhihu.com/captcha.gif'
        time_stamp = int(1000 * time.time())
        captcha = self.session.get(captcha_url, params={'r': time_stamp, 'type': 'login'})
        print 'http://www.zhihu.com/captcha.gif?r='+str(time_stamp)+'&type=login'
        with open('captcha.gif', 'wb') as f:
            for chunk in captcha:
                f.write(chunk)

    def log_in(self):
        """post the user information to get the status of logged in"""
        if self.username is None or  self.password is None:
            raise Exception('No username/password')
        print "Logging in..."
        data = {'email': self.username,
                'password': self.password,
                'remember_me': 'false',
                }
        while True:
            response = self.session.post(url='http://www.zhihu.com/login/email',
                                         data=data)
            try:
                response_dict = json.loads(response.content)
            except ValueError, e:
                print e
                print response.content

            if response_dict['msg'] == u"\u63d0\u4ea4\u8fc7\u5feb\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5 :(":
                print 'need to wait for 5 sec...'
                time.sleep(5)
            elif response_dict['msg'] == u'\u767b\u9646\u6210\u529f':
                print "Login succeed!"
                break
            else:
                print response_dict
                if self.input_captcha:
                    self.get_captcha()
                    print 'enter captcha'
                    data['captcha'] = raw_input()
                else:
                    print 'need captcha, wait for 30 mins to skip captcha'
                    time.sleep(1800)

    def get_content(self, url):
        return self.session.get(url=url).content


if __name__ == '__main__':
    client = Client()
    client.get_captcha()
