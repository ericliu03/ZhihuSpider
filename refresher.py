from threading import Thread, Event
from data_model import Profile
import traceback
import logging
from bs4 import BeautifulSoup
from requests import ConnectionError
import json


class Refresher(Thread):
    def __init__(self, worker_id, queue, client, db):
        super(Refresher, self).__init__()
        self.worker_id = worker_id
        self.queue = queue
        self.client = client
        self.db = db

        self._stop = Event()
        self.debug = []

    def find_user_info(self, content=None):
        user = Profile('city-zhou-kan', '', '', '', '', '')
        if not content:
            user = self.queue.get()
            content = self.client.get_content('http://www.zhihu.com/people/' + user.get_info('user_name'))

        info_dict = {'user_name': user.get_info('user_name')}

        self.debug = content
        soup = BeautifulSoup(content, "lxml")

        info_dict['num_followers'] = soup.find(attrs={'href': '/people/' + user.get_info('user_name') + '/followers'}).find('strong').contents[0]
        info_dict['num_followees'] = soup.find(attrs={'href': '/people/' + user.get_info('user_name') + '/followees'}).find('strong').contents[0]

        # narrow down the scope of contect to only this user
        soup = soup.find(attrs={'class': 'zm-profile-header ProfileCard'})

        info_dict['num_agree'] = soup.find(attrs={'class': "zm-profile-header-user-agree"}).find('strong').contents[0]

        info_dict['num_thanks'] = soup.find(attrs={'class': "zm-profile-header-user-thanks"}).find('strong').contents[0]

        description = soup.find(attrs={'class': 'zm-profile-header-description editable-group '})
        info_dict['description'] = description.find(attrs={'class': 'content'}).contents[0] if description else ''

        short_description = soup.find(attrs={'class': 'bio'})
        info_dict['short_description'] = short_description.contents[0] if short_description else ''

        info_dict['user_hash'] = soup.find(attrs={'data-follow': 'm:button'})['data-id']
        # temp = soup.find(attrs={'class': 'title-section ellipsis'}) # this tab contains title and short description

        info_dict['user_title'] = soup.find(attrs={'class': 'name'}).contents[0]

        info_dict['avatar_url'] = soup.find(attrs={'class': 'Avatar Avatar--l'})['srcset'][:-3]

        print 'user {} refreshed!'.format(info_dict['user_name'])
        # print json.dumps(info_dict, indent=4)
        self.db.insert(info_dict)

    def run(self):
        print 'Spider No.', self.worker_id, ' is on the way!'
        while not self._stop.is_set():
            try:
                self.find_user_info()
            # except ConnectionError:
            #     e = traceback.format_exc()
            #     print 'worker', self.worker_id, e
            #     logging.error(e)
            #     break
            except Exception:
                e = traceback.format_exc()
                print 'worker', self.worker_id, e
                print self.debug
                logging.error(e)

    def stop(self):
        self._stop.set()


if __name__ == '__main__':
    s = Refresher(None, None, None, None)

    with open('test.html', 'r') as f:
        print s.find_user_info(f.read())