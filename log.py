import logging
import time


class TestLog(object):
    def __init__(self):
        self.logger = logging.getLogger('CMC')
        self.logger.setLevel(logging.DEBUG)
        self.log_time = time.strftime("%Y_%m_%d")
        self.log_path = f'log_{self.log_time}.log'

        fh = logging.FileHandler(self.log_path, 'a', encoding='utf-8')  # 这个是python3的
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]  %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        fh.close()

    def get_log(self):
        return self.logger


logger = TestLog().get_log()
