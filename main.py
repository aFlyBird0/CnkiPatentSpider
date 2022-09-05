import logging

from spider import Spider
from status_manager import StatusManager

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sm = StatusManager('./code/test.txt', '2021-03-30', '2021-12-31')
    print(sm.list_codes())
    # for item in sm.list_date_and_codes():
    #     print(item)

    # 这里的参数建议结合代理好好调一下
    # 也可以把重试次数，睡眠时间等信息放到 settings.py 中
    spider = Spider(max_retry=10, sleep_time_min=0.5)
    spider.crawl_all(sm)
