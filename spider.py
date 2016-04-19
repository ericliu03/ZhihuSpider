from threading import Thread, Event
from data_model import Profile
from bs4 import BeautifulSoup
from requests import ConnectionError
import traceback
import logging


class Spider(Thread):
    def __init__(self, worker_id, queue, client, db, safe_set):
        super(Spider, self).__init__()
        self.queue = queue
        self.client = client
        self.db = db
        self.worker_id = worker_id
        self.safe_set = safe_set
        self._stop = Event()

    def find_user_info(self, test_file=None):
        """"Get the detailed info of this user got from queue, and get all it's followees's basic info, and put them into
        queue"""
        if test_file is not None:
            user = Profile('Kirio', 'test', 'test', 'test', 'test')
            content = test_file
        else:
            user = self.queue.get()
            content = self.client.get_content('http://www.zhihu.com/people/' + user.get_info('user_name') + '/followees')

        soup = BeautifulSoup(content, "lxml")

        # get detailed user information
        num_followers = soup.find(attrs={'href': '/people/' + user.get_info('user_name') + '/followers'}).find('strong').contents[0]
        num_followees = soup.find(attrs={'href': '/people/' + user.get_info('user_name') + '/followees'}).find('strong').contents[0]
        num_agree = soup.find(attrs={'class': "zm-profile-header-user-agree"}).find('strong').contents[0]
        num_thanks = soup.find(attrs={'class': "zm-profile-header-user-thanks"}).find('strong').contents[0]
        description = soup.find(attrs={'class': 'zm-profile-header-description editable-group '})

        if description is not None:
            description = description.find(attrs={'class': 'content'}).contents[0]
        else:
            description = ''

        # after got all info we need, save the user to database
        user.add_detailed_info(num_followers, num_followees, num_agree, num_thanks, description)
        self.db.insert(user.info)
        user.save()  # right now used for printing

        followees = soup.find_all(attrs={'class': "zm-profile-card zm-profile-section-item zg-clear no-hovercard"})
        seen_users = 0
        for followee in followees:
            # for each followee, get the basic information and put them into the queue
            user_hash = followee.find(attrs={'data-follow': 'm:button'})['data-id']
            # if already got this user, skip
            if user_hash in self.safe_set:
                seen_users += 1
                continue
            else:
                self.safe_set.add(user_hash)
            short_description = followee.find(attrs={'class': 'zg-big-gray'}).contents
            # get basic info of this user's followees
            temp = followee.find(attrs={'class': 'zm-item-link-avatar'})
            user_name = temp['href'][8:]  # user name (id)
            user_title = temp['title']  # user nickname
            avatar_url = temp.find(attrs={'class': 'zm-item-img-avatar'})['src']
            avatar_url = avatar_url[:-5] + 'xl.png'

            if len(short_description) == 0:
                short_description = ''
            else:
                short_description = short_description[0]
            self.queue.put(Profile(user_name, user_title, user_hash, avatar_url, short_description))
        logging.info('Number of seen users:' + str(seen_users))

    def run(self):
        print 'Spider No.', self.worker_id, ' is on the way!'
        while not self._stop.is_set():
            try:
                self.find_user_info()
            except Exception:
                e = traceback.format_exc()
                print 'worker', self.worker_id, e
                logging.error(e)
            except ConnectionError:
                e = traceback.format_exc()
                print 'worker', self.worker_id, e
                logging.error(e)
                break

    def stop(self):
        self._stop.set()

if __name__ == '__main__':
    s = Spider(None, None, None, None, None)

    with open('test.html', 'r') as f:
        print s.find_user_info(f.read())