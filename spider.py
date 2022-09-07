import logging
import math
import os
import random
import re
import time

from lxml import etree

import settings
from cookie import CookieUtil
from status_manager import StatusManager, lower_level_date_and_code



class Spider:
    def __init__(self, sleep_time_min=1, sleep_time_max=2, max_retry=5, proxy_bool=True):
        self.base_url = 'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=10&ID=&turnpage=1&tpagemode=L&dbPrefix=SCPD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0&'
        self.patent_content_pre_url = 'https://kns.cnki.net/kcms/detail/detail.aspx?dbcode=SCPD&dbname=SCPD%s&filename=%s'
        self.sleep_time_min = sleep_time_min  # 最短睡眠时间，单位秒
        self.sleep_time_max = sleep_time_max  # 最长睡眠时间，单位秒
        self.max_retry = max_retry  # 最大重试次数
        self.header_page = settings.headers_page
        self.proxy_bool = proxy_bool

    def crawl_all(self, sm: StatusManager):
        for date, code in sm.next_date_and_code():
            #self.crawl_one(date, code)
            self.crawl_tree(date, list(code), sm.codes_tree)

    def crawl_one(self, date, code):
        """
        爬取一个日期和一个分类号的专利页面
        :return:
        """
        # url_first = self.base_url % 1 尽量模拟真实浏览器操作
        url_first = 'https://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_result_aspx&isinEn=0&dbPrefix=SCPD&dbCatalog=%e4%b8%ad%e5%9b%bd%e4%b8%93%e5%88%a9%e6%95%b0%e6%8d%ae%e5%ba%93&ConfigFile=SCPD.xml&research=off&t=' + str(
            int(round(time.time() * 1000))) + '&keyValue=&S=1&sorttype='
        # 获取一个带有查询信息的cookie
        session = CookieUtil.get_session_with_search_info(date, code, self.proxy_bool)
        self.random_sleep()
        # session 保留用于每页查找
        page_num, patent_num, session = self.get_pages_meta(url_first, code, date, session)
        if page_num > 119:
            return False
        if page_num > 0 and patent_num > 0:
            logging.info("开始爬取 %s %s" % (date, code))
            os.makedirs("./data/%s/%s" % (date, code), exist_ok=True)
            with open("./data/%s/%s/meta.txt" % (date, code), "w", encoding="utf-8") as f:
                f.write(str(page_num) + "\n")
                f.write(str(patent_num))
            crawl_public_codes = []
            for page_response, page_num in self.get_pages(code, date, page_num, session):
                with open("./data/%s/%s/%s.html" % (date, code, page_num), "w", encoding="utf-8") as f:
                    f.write(page_response.text)
                # todo 这里我为了测试，把获取内容和解析页面 link 一起做掉了，应该拆开
                # 然后再一个个去读取文件夹，解析出 link 或者说公开号
                # todo 把 (date、code、公开号) 三元组 存到数据库里，并且加两个字段，供以后的获取详细内容用
                #  一个字段是否爬取详细内容并解析内上传到数据库成功，一个字段是该公开号一共被尝试爬过多少次
                for item in self.parse_page_links(page_response.text, page_num, code, date):
                    logging.debug(item)
                    crawl_public_codes.append(item)
            if len(crawl_public_codes) == patent_num:
                logging.info("专利号数量比对成功，开始存储")
                with open("./data/public_codes.txt", 'a', encoding='utf-8') as f:
                    for item in crawl_public_codes:
                        f.writelines(date + ',' + code + ',' + item)
                        f.write('\r\n')
            else:
                logging.error("专利号数量比对失败, %s %s" % (date, code))
                self.err_record(date, code)
        return True

    # 爬树
    def crawl_tree(self,date, key_codes, tree):
        logging.info('开始爬code-tree %s' %(date))
        for key_code in key_codes:
            if tree == {}:
                if self.crawl_one(date,key_code):
                    logging.error("%s 的 %s 页数超过120页，不予爬取" % (key_code, date))
                    self.err_record(date,key_code)
                else:
                    logging.info(key_code+ ' get')
            else:
                if not self.crawl_one(date, key_code):
                    for keys_child, tree_child in lower_level_date_and_code(tree[key_code]):
                        self.crawl_tree(date, keys_child, tree_child)
                else:
                    logging.info(key_code+ ' get')

    def get_pages_meta(self, url_first, code, date, session):
        """
        获取专利页面页面的元数据，包含总页数，总文献数等，并返回一个元组
        :param url_first:
        :param code:
        :param date:
        :param cookie:
        :return: (page_num, patent_num) 页数和文献数，如果出错，返回 (-1, -1)
        """
        # 先请求一次，获取总页数和总文献数等信息
        self.header_page["Referer"] = "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCPD"
        session.headers = self.header_page
        res = session.get(url_first)
        # res = requests.get(url_first, cookies=cookie)
        # 重试最大次数
        success = False
        for i in range(self.max_retry):
            # 页面获取失败，重爬，基本上所有的空白页大小都小于 3500 这个值
            if res.status_code != 200 or int(res.headers['content-length']) < 3500:
                logging.error("爬取到空白页 %s %s，第%d次尝试" % (date, code, i))
                # 空白页的原因很有可能是因为太频繁，这里单独长时间等待
                time.sleep(3)
                session = CookieUtil.get_session_with_search_info(date, code, self.proxy_bool)
                res = session.get(url_first)
            else:
                html = etree.HTML(res.text)
                pager_title_cells = html.xpath('//div[@class="pagerTitleCell"]/text()')
                # 页面解析失败，说明页面获取到了，但内容不对重爬
                if len(pager_title_cells) == 0:
                    # print(response.text)
                    # 这里的url一定不是空的，如果是空的话前面已经return了不用担心
                    # 虽然已经处理了空白页，但是仍然保留。
                    logging.error("解析专利页数和篇数信息错误 %s %s %s %s" % (date, code, url_first, res.text))
                    continue
                page = pager_title_cells[0].strip()
                patent_num = int(re.findall(r'\d+', page.replace(',', ''))[0])  # 文献数
                page_num = math.ceil(patent_num / 50)  # 算出页数
                logging.info("%s %s 共有：%d篇文献, %d页" % (code, date, patent_num, page_num))
                self.header_page['Referer'] = url_first
                # 返回重新请求或者原来的seesion
                return page_num, patent_num, session

        # 实际还应该记录 date, code，用来重爬，建议放数据库里
        # 然后 status_manger 加一个从数据库读取 date, code 列表的方法
        # 不断地去爬这个列表，成功后标记一下
        logging.error("专利页面请求或请求出现错误 %s %s %s" % (date, code, url_first))
        # os.makedirs("./err/%s/%s" % (date, code), exist_ok=True)
        # with open("./err/%s/%s/error.html" % (date, code), "w", encoding="utf-8") as f:
        #     f.write(res.text)
        self.err_record(date, code)
        return -1, -1, session

    def get_pages(self, code, date, page_num, session):
        """
        获取所有专利的搜索结果页面，并返回一个生成器
        :param code:
        :param date:
        :param page_num:
        :return:
        """
        # 使用上次请求的cookie，否则无法翻页成功
        # cookies_now = CookieUtil.get_cookies_with_search_info(date, code)
        # 获取上次请求的使用的proxy，这次请求用的cookie和proxy都和以前一致
        # proxyString = response.meta['proxy']
        session.headers = self.header_page
        for i in range(1, page_num + 1):
            self.random_sleep()
            # 超过15页换session
            if i % 13 == 0:
                session = CookieUtil.get_session_with_search_info(date, code, self.proxy_bool)
            url = self.base_url % i
            # response = requests.get(url, cookies=cookies_now)
            response = session.get(url)
            for j in range(self.max_retry):
                if response.status_code == 200 and int(response.headers['content-length']) > 3500:
                    break
                else:
                    logging.info("翻页错误 %s %s, 第 %d 次尝试" % (date, code, j))
                    self.random_sleep()
                    session = CookieUtil.get_session_with_search_info(date, code, self.proxy_bool)
                    response = session.get(url)
            if response.status_code != 200:
                # 里面的错误结果可能重复
                self.err_record(date, code)
                logging.error("专利页面请求出现错误 %s %s %s %s" % (date, code, url, response.text))
                continue
            # 迭代返回页面内容和页面编号
            self.header_page['Referer'] = url
            yield response, i
        session.close()

    def parse_page_links(self, response_text, page_num, code, date):
        """
        解析专利搜索结果的某一页，获取该页的所有专利的链接
        :param response_text:
        :param page_num:
        :param code:
        :param date:
        :return:
        """
        links_html = etree.HTML(response_text).xpath('//a[@class="fz14"]/@href')  # 返回链接地址href列表
        if len(links_html) == 0:
            return
        logging.info("日期：%s,学科分类：%s，第%d页有%d个专利" % (date, code, page_num, len(links_html)))

        for j in range(len(links_html)):
            patent_code = re.search(r'filename=(.*)$', links_html[j]).group(1)
            # 这里也可以不返回 link，直接返回 patent_code
            # link = self.patent_content_pre_url % (date[0:4], patent_code)
            yield patent_code

    def random_sleep(self):
        """
        在一个时间区间内随机睡眠一段时间
        :return:
        """
        time.sleep(random.randint(int(self.sleep_time_min * 1000), int(self.sleep_time_max * 1000)) / 1000.0)

    def err_record(self, date, code):
        os.makedirs("./err/", exist_ok=True)
        with open("./err/code_err.txt", "a+", encoding="utf-8") as f:
            f.writelines(date + ',' + code[0])
            f.write('\r\n')