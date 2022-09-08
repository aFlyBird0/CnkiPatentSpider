import csv
import logging

from pymysql import *

import settings


def get_orgin_data(csv_path):
    csv_reader = csv.reader(open(csv_path))
    all_code = {}
    for public_cdoe, author_code in csv_reader:
        if public_cdoe != '':
            all_code.update({public_cdoe:False})
        if author_code != '':
            all_code.update({author_code: False})
    return all_code

def get_crawl_data(meta_path):
    all_meta_data = []
    with open(meta_path, 'r') as f:
        for i in f.readlines():
            date, code, public_code = i.strip().split(',')
            all_meta_data.append((date,code,public_code))
    return all_meta_data

def upload_new_data(all_code, all_meta_data):
    conn = connect(host=settings.mysql_connect['host'], port=settings.mysql_connect['port'], user=settings.mysql_connect['user'], password=settings.mysql_connect['password'],
                   database=settings.mysql_connect['db'], charset=settings.mysql_connect['charset'])

    new_data = []
    for single_task in all_meta_data:
        if all_code.get(single_task[2], True):
            new_data.append(single_task)

    cur = conn.cursor()
    sql = 'insert into tasks (`date`, `code`, `public_code`) values (%s, %s, %s) on duplicate key update date=values(date), code=values(code), public_code=values(public_code)'

    cur.executemany(sql, new_data)
    conn.commit()
    cur.close()
    conn.close()
    print('Ok, go step 3')


if __name__ == '__main__':
    all_code = get_orgin_data('/Users/black/Downloads/itech4u_patent.csv')
    print('all_code结束')
    all_meta_data = get_crawl_data('./data/public_codes.txt')
    print('all_mata_data结束')
    upload_new_data(all_code,all_meta_data)