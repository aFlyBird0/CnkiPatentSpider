import time
import requests
from requests.adapters import HTTPAdapter, Retry
import settings
from util import sessionn_throw_unknown_errors

class CookieUtil:
    @classmethod
    def get_session_with_search_info(cls, date, code, proxy_bool):
        '''
        返回带有查询信息的session
        根据日期，分类代码获取cookies,翻页时必须要有cookie
        :param date:
        :param code:
        :param proxy_bool:
        :return: session
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
        session = requests.session()
        # 使用 requests 模块中的 Retry, 处理请求异常
        # 使用 urllib3 的 Retry，因为 requests 的 Retry 无法处理 readout
        session.mount('https://', HTTPAdapter(
            max_retries=Retry(total=settings.MAX_RETRY,read=settings.MAX_RETRY, allowed_methods=(['GET', 'POST']), backoff_factor=0.1)))
        session.mount('http://', HTTPAdapter(
            max_retries=Retry(total=settings.MAX_RETRY, read=settings.MAX_RETRY, allowed_methods=(['GET', 'POST']), backoff_factor=0.1)))
        session.headers = headers
        session.trust_env = False
        if proxy_bool:
            session.proxies.update(settings.proxies)
        session = sessionn_throw_unknown_errors(session=session, url=search_url, params=params ,date=date, code=code)

        return session