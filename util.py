import logging
import os
import settings


def err_record(date, code):
    os.makedirs("./err/", exist_ok=True)
    with open("./err/code_err.txt", "a+", encoding="utf-8") as f:
        f.write(date + ',' + code[0])
        f.write('\n')

def sessionn_throw_unknown_errors(session, url, date, code, params={}, timeout=(3,3)):
    for http_i in range(settings.MAX_RETRY):
        try:
            session.get(url, params=params, timeout = timeout)
        except:
            logging.info('未知请求错误, 第 %d 次尝试' % (http_i))
        else:
            return session
    err_record(date=date, code=code)
    logging.error("未知请求错误, %s %s" % (date, code))

def session_get_thro_unknown_errors(session, url, date, code, timeout=(3,3)):
    for http_i in range(settings.MAX_RETRY):
        try:
            res = session.get(url, timeout=timeout)
        except:
            logging.info('未知请求错误, 第 %d 次尝试' % (http_i))
        else:
            return res
    err_record(date=date, code=code)
    logging.error("未知请求错误, %s %s" % (date, code))