import time
import requests


class CookieUtil:
    @classmethod
    def get_cookies_with_search_info(cls, date, code):
        '''
        返回带有查询信息的cookies
        根据日期，分类代码获取cookies,翻页时必须要有cookie
        :param date:
        :param code:
        :param proxy:
        :return:
        '''
        search_url = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
        times = time.strftime('%a %b %d %Y %H:%M:%S') + ' GMT+0800 (中国标准时间)'
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "kns.cnki.net",
            "Origin": "https://kns.cnki.net",
            "Referer": "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCPD",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }
        params = {
            "action": "",
            "NaviCode": code,
            "ua": "1.21",
            "isinEn": "0",
            "PageName": "ASP.brief_result_aspx",
            "DbPrefix": "SCPD",
            "DbCatalog": "中国专利数据库",
            "ConfigFile": "SCPD.xml",
            "db_opt": "SCOD",
            "db_value": "中国专利数据库",
            "date_gkr_from": date,
            "date_gkr_to": date,
            "his": '0',
            '__': times
        }
        session_response = requests.get(search_url, headers=headers, params=params)
        cookies = requests.utils.dict_from_cookiejar(session_response.cookies)
        return cookies