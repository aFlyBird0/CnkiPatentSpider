import logging

import settings
from spider import Spider
from status_manager import StatusManager

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format = '%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
                        datefmt  = '%Y-%m-%d %A %H:%M:%S')
    sm = StatusManager('./code/prod.txt', '2021-01-01', '2021-01-31')
    # 这里的参数建议结合代理好好调一下
    # 也可以把重试次数，睡眠时间等信息放到 settings.py 中
    spider = Spider(max_retry=settings.MAX_RETRY, sleep_time_min=settings.SLEEP_TIME_MIN, proxy_bool=settings.PROXY_BOOL)
    spider.crawl_all(sm)
