# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import logging

from spider import Spider
from status_manager import StatusManager


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print_hi('PyCharm')
    sm = StatusManager('./code/test.txt', '2021-01-01', '2021-12-31')
    print(sm.list_codes())
    # for item in sm.list_date_and_codes():
    #     print(item)

    spider = Spider()
    spider.crawl_all(sm)
