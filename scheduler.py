from spider import Spider
from data_model import Profile, SafeSet
from http_client import Client
from Queue import Queue
from dbaccessor import DBAccessor
from datetime import datetime
import time
import pickle
import os.path
import logging
import sys
from abc import ABCMeta, abstractmethod

MY_USERNAME = 'liu-yang-26-15'
MY_ID = '23c76e145e5fcbd5da3402f39c8eb56e'
PROXIES = ['117.135.250.132:82', '117.135.250.133:81', '61.153.17.62:1080', '117.135.251.131:80', '117.135.251.135:80',
           '117.135.251.134:83', '117.135.251.136:80', '183.61.236.54:3128', '117.135.251.133:81','120.198.233.211:80']


class Scheduler(object):
    __metaclass__ = ABCMeta

    def __init__(self, use_proxy, db_name, db_collection, num_threads):

        self.use_proxy = use_proxy
        self.num_threads = num_threads

        self.db = DBAccessor(db_name, db_collection)
        self.queue = Queue()
        self.workers = None
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='./log/myapp.log')

    @abstractmethod
    def create_thread(self, index):
        pass

    @abstractmethod
    def get_worker_object(self, **kwargs):
        pass

    @abstractmethod
    def save_queue(self):
        pass

    @abstractmethod
    def load_data_to_queue(self):
        pass

    @abstractmethod
    def log_tick(self, dead_thread):
        pass

    def create_threads(self):
        threads = []
        for index in xrange(self.num_threads):
            print 'Starting spider No.', index
            if self.use_proxy or index == 0:
                new_client = self.create_thread(index)
            else:
                new_client = threads[index - 1].client
            threads.append(self.get_worker_object(index=index, new_client=new_client))

        for i in xrange(self.num_threads):
            threads[i].start()
        return threads

    def tick(self):
        dead_thread = 0
        for index, thread in enumerate(self.workers):
            if not thread.isAlive():
                if self.use_proxy:
                    logging.error(str(datetime.now()) + ': Thread ' + str(index) + ' is dead, try to reactivate...')
                    workers[index] = self.create_thread(index)
                    workers[index].start()
                    dead_thread += 1
                else:
                    logging.info('all thread dead, wait for 3 mins before reconnect')
                    time.sleep(180)
                    workers = self.create_threads()
        self.log_tick(dead_thread)

    def graceful_shutdown(self, *args):
        """store the users in queue to a file"""
        print 'Starting graceful shutdown....'
        logging.warning('Starting graceful shutdown....')
        for worker in self.workers:
            worker.stop()
        for worker in self.workers:
            worker.join()
            logging.info('Thread ' + str(worker.worker_id) + ' stopped!')
        self.save_queue()
        logging.info('Program terminated!')
        print 'Program shutdown!'
        sys.exit(0)


class SpiderScheduler(Scheduler):
    def __init__(self, username, password, use_proxy=False, db_name='zhihu', db_collection='users_test3',
                 queue_file='temp_queue.dat', num_threads=2, input_captcha=False):
        super(SpiderScheduler, self).__init__(use_proxy=use_proxy, db_name=db_name,
                                              db_collection=db_collection, num_threads=num_threads)
        self.username = username
        self.password = password
        self.queue_file = queue_file
        self.input_captcha = input_captcha
        self.safe_set = SafeSet(self.db)

        self.load_data_to_queue()
        self.workers = self.create_threads()

    def load_data_to_queue(self):
        print 'Loading queue from last time...'
        if os.path.isfile(self.queue_file):
            with open(self.queue_file, 'rb') as f:
                users_in_queue = pickle.load(f)
            for each in users_in_queue:
                self.queue.put(each)
            print 'Succeed with ', len(users_in_queue), ' items!'
        else:
            start_point = Profile(MY_USERNAME, u'liuyang', MY_ID, 'http://pic1.zhimg.com/da8e974dc_m.jpg', 'test')
            self.queue.put(start_point)
            print 'No file exist, using start point!'

    def create_thread(self, index):
        proxy = 'http://' + PROXIES[index] if self.use_proxy else None
        new_client = Client(proxy=proxy, username=self.username, password=self.password,
                            input_captcha=self.input_captcha)
        new_client.log_in()
        return new_client

    def get_worker_object(self, **kwargs):
        return Spider('worker: ' + str(kwargs['index']), self.queue, kwargs['new_client'], self.db, self.safe_set)

    def save_queue(self):
        """Queue can not be pickled, so transform a queue into a list to store"""
        print 'Storing current queue!'
        users_in_queue = []
        while not self.queue.empty():
            users_in_queue.append(self.queue.get())
        with open(self.queue_file, 'wb') as f:
            pickle.dump(users_in_queue, f)
        print len(users_in_queue), 'users in the queue stored in file!'

    def log_tick(self, dead_thread):
        logging.info('Collected User:' + str(self.db.get_user_number()))
        logging.info('healthy threads: %d/%d' % (self.num_threads - dead_thread, self.num_threads))
        print datetime.now(), 'healthy threads: %d/%d' % (self.num_threads - dead_thread, self.num_threads), \
            'Collected User:', self.db.get_user_number()


class RefresherScheduler(Scheduler):
    def __init__(self, use_proxy=False, db_name='zhihu', db_collection='users_refresh', num_threads=2):
        super(RefresherScheduler, self).__init__(use_proxy=use_proxy, db_name=db_name,
                                                 db_collection=db_collection, num_threads=num_threads)
        self.workers = self.create_threads()
        self.count = 0

    def create_thread(self, index):
        pass

    def get_worker_object(self, **kwargs):
        pass

    def save_queue(self):
        pass

    def load_data_to_queue(self):
        print "Getting data that needed to be refreshed from db to queue..."
        temp_db = DBAccessor(db='zhihu', collection='users_test2')
        cursor = temp_db.find()
        for each in cursor:
            self.queue.put(Profile(info_dict=each))
            self.count += 1
        print "Succeed with {} items...".format(self.count)

    def log_tick(self, dead_thread):
        logging.info("{} of users remaining...".format(self.count))
        logging.info('healthy threads: %d/%d' % (self.num_threads - dead_thread, self.num_threads))
        print datetime.now(), 'healthy threads: %d/%d' % (self.num_threads - dead_thread, self.num_threads), \
            "{} of users remaining...".format(self.count)
