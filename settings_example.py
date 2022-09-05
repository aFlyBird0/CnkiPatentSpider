mysql_connect = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'db': 'cnki',
    'charset': 'utf8mb4',
}

kuai_tunnel = 'xxx.xxx.com:xxxx'
kuai_username = ''
kuai_password = ''

headers_page = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "close",
    "DNT": "1",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "kns.cnki.net",
    "Origin": "https://kns.cnki.net",
    "Referer": "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCPD",
    "Sec-Fetch-Dest": "iframe",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Sec-GPC": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

MAX_RETRY=10
SLEEP_TIME_MIN=0.5
PROXY_BOOL=True