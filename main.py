from scheduler import SpiderScheduler, Scheduler, RefresherScheduler
import time
import logging
import signal
import traceback


def initialize():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='./log/myapp.log')

    input_user, input_password = ['user_name', 'password']

    def raise_sigterm_exception(*args):
        raise Exception('Caught SIGTERM!')
    signal.signal(signal.SIGTERM, raise_sigterm_exception)
    return RefresherScheduler(use_proxy=True, num_threads=9)
    # return SpiderScheduler(username=input_user, password=input_password, use_proxy=False,
    #                        num_threads=3, input_captcha=True, db_collection='users_test3')


def main():
    scheduler = initialize()
    try:
        while True:
            scheduler.tick()
            time.sleep(10)
    except (Exception, KeyboardInterrupt):
        e = traceback.format_exc()
        print e
        logging.error(e)
    finally:
        scheduler.graceful_shutdown()

if __name__ == '__main__':
    main()


