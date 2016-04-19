import requests
import json
import time




def get_captcha(session):
    """Download captcha to a image"""
    print 'Getting captcha...'
    captcha_url = 'http://www.zhihu.com/captcha.gif'
    captcha = session.get(captcha_url, stream=True, params={'r': int(1000 * time.time()), 'type': 'login'})
    with open('captcha.gif', 'wb') as f:
        for line in captcha.iter_content(10):
            f.write(line)

def log_in(session):
    """post the user information to get the status of logged in"""
    print "Logging in..."
    data = {'email': 'erickliu@vip.qq.com',
            'password': '199233',
            'remember_me': 'false',
            # seems included in cookies is enough
            # '_xsrf': self._xsrf
            }
    while True:
        response = session.post(url='http://www.zhihu.com/login/email',
                                     data=data)
        response_dict = json.loads(response.content)
        if response_dict['msg'] == u"\u63d0\u4ea4\u8fc7\u5feb\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5 :(":
            print 'need to wait for 5 sec...'
            time.sleep(5)
        elif response_dict['msg'] == u'\u767b\u9646\u6210\u529f':
            break
        else:
            print response_dict
            print 'captcha wrong, try again'
        get_captcha(session)
        print 'enter captcha'
        data['captcha'] = raw_input()
    print "Login succeed!"

def request(session):
    resp = session.get(url='http://www.zhihu.com/people/Kirio/followees')
    print resp.content


if __name__ == '__main__':
    proxies = {
        'http': 'http://117.135.251.134:83',
    }
    session1 = requests.Session()
    session1.proxies.update(proxies)

    proxies = {
        'http': 'http://117.135.251.135:80',
    }
    session2 = requests.Session()
    session2.proxies.update(proxies)

    # session1.get(url='http://www.baidu.com')
    log_in(session1)
    log_in(session2)

    request(session1)
    request(session2)
