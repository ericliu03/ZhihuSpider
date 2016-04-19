import threading
import logging


class Profile:
    def __init__(self, user_name=None, user_title=None, user_hash=None, avatar_url=None, short_description=None, info_dict=None):
        if info_dict:
            self.info = info_dict
        else:
            self.info = {
                'user_name': str(user_name),
                'user_title': user_title.encode('utf-8'),
                'user_hash': str(user_hash),
                'avatar_url': str(avatar_url),
                'short_description': short_description.encode('utf-8')
            }

    def add_detailed_info(self, num_followers, num_followees, num_agree, num_thanks, description):
        self.info['num_followers'] = int(num_followers)
        self.info['num_followees'] = int(num_followees)
        self.info['num_agree'] = int(num_agree)
        self.info['num_thanks'] = int(num_thanks)
        self.info['description'] = description.encode('utf-8')

    def get_info(self, key):
        return self.info[key]

    # def get_html_content(self):
    #     response = self.session.get(url='https://www.zhihu.com/people/' + self.info['user_name'] + '/followees')
    #     return response.content

    def save(self):
        logging.info('User: '+ self.info['user_name'] + ' stored!')
        # self.db.insert(self.info)

    def __str__(self):
        return str(self.info)


class SafeSet(set):
    def __init__(self, db):
        print 'Building the set...'
        cursor = db.find({}, {'_id': 0, 'user_hash': 1})
        current_users = []
        for each in cursor:
            current_users.append(each['user_hash'])
        super(SafeSet, self).__init__(current_users)
        print 'set built succeed, number of existing users: ', len(self)
        self.lock = threading.Lock()

    def add(self, x):
        with self.lock:
            return super(SafeSet, self).add(x)

    def __contains__(self, x):
        with self.lock:
            return super(SafeSet, self).__contains__(x)


