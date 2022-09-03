import logging
import math
import os
import random
import re
import time

from lxml import etree

import requests

from cookie import CookieUtil
from status_manager import StatusManager


class Spider:
    def __init__(self, sleep_time_min=0.1, sleep_time_max=1):
        self.base_url = 'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=10&ID=&turnpage=1&tpagemode=L&dbPrefix=SCPD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0&'
        self.patent_content_pre_url = 'https://kns.cnki.net/kcms/detail/detail.aspx?dbcode=SCPD&dbname=SCPD%s&filename=%s'
        self.sleep_time_min = sleep_time_min    # 最短睡眠时间，单位秒
        self.sleep_time_max = sleep_time_max    # 最长睡眠时间，单位秒

    def crawl_all(self, sm: StatusManager):
        for date, code in sm.list_date_and_codes():
            self.crawl_one(date, code)

    def crawl_one(self, date, code):
        """
        爬取一个日期和一个分类号的专利页面
        :return:
        """
        url_first = self.base_url % 1

        # 获取一个带有查询信息的cookie
        # todo 为这个 cookie 获取函数加个代理
        cookie = CookieUtil.get_cookies_with_search_info(date, code)
        self.random_sleep()

        page_num, patent_num = self.get_pages_meta(url_first, code, date, cookie)
        if page_num > 0 and patent_num > 0:
            print("开始爬取 %s %s" % (date, code))
            os.makedirs("./data/%s/%s" % (date, code), exist_ok=True)
            with open("./data/%s/%s/meta.txt" % (date, code), "w", encoding="utf-8") as f:
                f.write(str(page_num) + "\n")
                f.write(str(patent_num))
            for page_response, page_num in self.get_pages(code, date, cookie, page_num):
                with open("./data/%s/%s/%s.html" % (date, code, page_num), "w", encoding="utf-8") as f:
                    f.write(page_response.text)
                # todo 这里我为了测试，把获取内容和解析页面 link 一起做掉了，应该拆开
                # 先把所有的有效的 page_response.text 存起来，文件夹结构弄好
                # 然后再一个个去读取文件夹，解析出 link 或者说公开号，再存到数据库里
                print(self.parse_page_links(page_response, page_num, code, date))

    def get_pages_meta(self, url_first, code, date, cookie):
        """
        获取专利页面页面的元数据，包含总页数，总文献数等，并返回一个元组
        :param url_first:
        :param code:
        :param date:
        :param cookie:
        :return: (page_num, patent_num) 页数和文献数，如果出错，返回 (-1, -1)
        """
        # 先请求一次，获取总页数和总文献数等信息
        res = requests.get(url_first, cookies=cookie)
        if res.status_code != 200:
            # todo 重试，达到最大重试次数后，在特定文件或数据库中记录错误结果
            logging.error("专利页面请求出现错误 %s %s %s %s" % (date, code, url_first, res.text))
            return -1, -1

        html = etree.HTML(res.text)
        pager_title_cells = html.xpath('//div[@class="pagerTitleCell"]/text()')
        if len(pager_title_cells) == 0:
            # print(response.text)
            # 这里的url一定不是空的，如果是空的话前面已经return了不用担心
            # todo 重试，达到最大重试次数后，在特定文件或数据库中记录错误结果
            # logging.error("解析专利页数和篇数信息错误 %s %s %s %s" % (date, code, url_first, res.text))
            return -1, -1
        page = pager_title_cells[0].strip()
        patent_num = int(re.findall(r'\d+', page.replace(',', ''))[0])  # 文献数
        page_num = math.ceil(patent_num / 50)  # 算出页数
        logging.info("%s %s 共有：%d篇文献, %d页" % (code, date, patent_num, page_num))
        if page_num > 120:
            # todo 重试，达到最大重试次数后，在特定文件或数据库中记录错误结果
            logging.error("%s 的 %s 页数超过120页，不予爬取" % (code, date))
            return -1, -1

        return page_num, patent_num

    def get_pages(self, code, date, cookies, page_num):
        """
        获取所有专利的搜索结果页面，并返回一个生成器
        :param code:
        :param date:
        :param cookies:
        :param page_num:
        :return:
        """
        # 使用上次请求的cookie，否则无法翻页成功
        cookies_now = cookies
        # 获取上次请求的使用的proxy，这次请求用的cookie和proxy都和以前一致
        # proxyString = response.meta['proxy']

        for i in range(1, page_num + 1):
            self.random_sleep()
            # 超过15页换cookie
            if i % 13 == 0:
                cookies_now = CookieUtil.get_cookies_with_search_info(date, code)
            url = self.base_url % i

            response = requests.get(url, cookies=cookies_now)
            # todo 这里要改一下：多次重试，成功后就 yield, 否则要记录一下错误
            if response.status_code != 200:
                logging.error("专利页面请求出现错误 %s %s %s %s" % (date, code, url, response.text))
                continue
            # 迭代返回页面内容和页面编号
            yield response, i

    def parse_page_links(self, response: requests.models.Response, page_num, code, date):
        """
        解析专利搜索结果的某一页，获取该页的所有专利的链接
        :param response:
        :param page_num:
        :param code:
        :param date:
        :return:
        """
        if response.status_code != 200:
            logging.error("专利页面请求出现错误 %s %s %s %s" % (date, code, response.url, response.text))
            return
        links_html = etree.HTML(response.text).xpath('//a[@class="fz14"]/@href')  # 返回链接地址href列表
        if len(links_html) == 0:
            return
        logging.info("日期：%s,学科分类：%s，第%d页有%d个专利" % (date, code, page_num + 1, len(links_html)))

        public_codes = []
        for j in range(len(links_html)):
            patent_code = re.search(r'filename=(.*)$', links_html[j]).group(1)
            # 这里也可以不返回 link，直接返回 patent_code
            # link = self.patent_content_pre_url % (date[0:4], patent_code)
            public_codes.append(patent_code)
        return public_codes

    # 在一个时间区间内随机睡眠一段时间
    def random_sleep(self):
        time.sleep(random.randint(int(self.sleep_time_min * 1000), int(self.sleep_time_max * 1000)) / 1000.0)
