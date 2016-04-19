from scheduler import SpiderScheduler
import time
import logging
import signal
import traceback


def main():
    input_user, input_password = ['erickliu@vip.qq.com', '199233']
    scheduler = SpiderScheduler(username=input_user, password=input_password, use_proxy=False,
                                num_threads=3, input_captcha=True, db_collection='users_test3')
    signal.signal(signal.SIGTERM, scheduler.graceful_shutdown)
    try:
        while True:
            scheduler.tick()
            time.sleep(10)
    except (Exception, KeyboardInterrupt):
        e = traceback.format_exc()
        print e
        logging.error(e)
        scheduler.graceful_shutdown()

if __name__ == '__main__':
    main()


