import logging
import os

from dateutil import rrule
from datetime import datetime
import yaml

class StatusManager:
    def __init__(self, code_path, start_date, end_date, status_path='status.txt', tree_path='./code/code_tree.yml'):
        self.code_path = code_path
        self.start_date = start_date
        self.end_date = end_date
        self.tree_path = tree_path
        self.all_code = self.load_codes()
        self.date_and_codes = list(self.list_date_and_codes())

        self.status_path = status_path
        # 获取上一次启动爬虫时的状态
        self.last_index = self.get_last_status_index()
        self.codes_tree = self.load_codes_tree()

    def next_date_and_code(self):
        if self.last_index == -1:
            self.last_index = 0

        # 从上一次的状态再爬一遍，相当于重复爬了一下之前的工作
        for i in range(self.last_index, len(self.date_and_codes)):
            current_date, current_code = self.date_and_codes[i]
            yield self.date_and_codes[i]
            self.update_status(current_date, current_code)

    def load_codes(self):
        """
        从文件中读取学科代码
        :return:
        """
        with open(self.code_path, 'r') as f:
            lines = f.read().splitlines()
            # 去除空行和空白符
            lines = [line.strip() for line in lines if line.strip()]
            return lines

    def list_codes(self):
        """
        列出所有的学科代码
        :return:
        """
        return self.all_code

    def get_last_status_index(self):
        """
        获取最后一次爬取的状态，返回在当前任务（日期-分类号）状态序列中的 下标
        :return:
        """
        # 判断是否存在状态文件，如果不存在，则创建一个空的状态文件
        if not os.path.exists(self.status_path):
            logging.info('状态文件不存在，将创建一个空的状态文件')
            with open(self.status_path, 'w') as f:
                f.write('')

        with open(self.status_path, 'r') as f:
            lines = f.read().splitlines()
            # 去除空行和空白符
            lines = [line.strip() for line in lines if line.strip()]
            if len(lines) == 0:
                logging.info('状态文件内容为空，将从第一个日期和学科分类号开始爬')
                # 返回 -1，这样爬虫就从第一个日期和学科分类号开始爬
                return -1
            else:
                last_date, last_code = lines[-1].split(',')
                # 从列表中找到对应的状态序号
                index = self.date_and_codes.index((last_date, last_code))
                # 如果找不到，就报错
                print('index', index)
                if index == -1:
                    logging.error(self.status_path + '中的状态' + last_date + ', ' + last_code + '不存在')
                return index

    def update_status(self, date, code):
        """
        追加当前状态到状态文件中
        :param date:
        :param code:
        :return:
        """
        with open(self.status_path, 'a') as f:
            f.write('{},{}\n'.format(date, code))

    def list_date_and_codes(self):
        """
        列出日期和学科代码的序列
        :return:
        """
        for date in list_dates(self.start_date, self.end_date):
            for code in self.all_code:
                yield date, code

    def load_codes_tree(self):
        """
        从文件中读取代码树
        :return:
        """
        with open(self.tree_path, 'r') as f:
            ayml = yaml.load(f.read(), Loader=yaml.Loader)
            return ayml



def lower_level_date_and_code(left_tree):
    """
    返回下层的code 和 tree
    :return:
    """
    for i in left_tree:
        if type(i) == str:
            yield [i],{}
        else:
            yield list(i.keys()), i.keys().mapping


def list_dates(start_date, end_date):
    """
    列出两个日期之间的所有日期
    :param start_date: 开始日期，格式为'2019-01-01'
    :param end_date: 结束日期，格式为'2019-01-01'
    :return:
    """
    if start_date > end_date:
        raise ValueError('start_date must be less than end_date')

    # 校验并转换日期格式
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    for dt in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
        yield dt.strftime('%Y-%m-%d')


if __name__ == '__main__':
    print('测试 StatusManager')
    sm = StatusManager('./code/test.txt', '2021-01-01', '2021-01-06')
    print(sm.list_codes())
    for item in sm.next_date_and_code():
        print(item)
