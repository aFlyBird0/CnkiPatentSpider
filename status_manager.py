from dateutil import rrule
from datetime import datetime


class StatusManager:
    def __init__(self, code_path, start_date, end_date):
        self.code_path = code_path
        self.start_date = start_date
        self.end_date = end_date
        self.all_code = self.load_codes()

    def load_codes(self):
        """
        读取学科代码
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

    def list_date_and_codes(self):
        """
        列出日期和学科代码的序列
        :return:
        """
        for date in list_dates(self.start_date, self.end_date):
            for code in self.all_code:
                yield date, code


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
