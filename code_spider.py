from lxml import etree

import cookie


base_url = 'https://kns.cnki.net/kns/request/NaviGroup.aspx?code=%s&tpinavigroup=SCODtpiresult&catalogName=&__=Mon Sep 05 2022 21:28:06 GMT+0800 (中国标准时间)'

session = cookie.CookieUtil.get_session_with_search_info("2021-01-01", "A", True)


def get_node(code, session, count):
    url = base_url % code
    res = session.get(url, timeout=1, headers=session.headers)
    html = etree.HTML(res.text)

    parent_node = []
    all_node = []
    for i in html.xpath('//input[@type="checkbox"]/@value'):
        all_node.append(str(i))
    # 有孩子所以love
    for love_node in html.xpath('//img[contains(@id, "first")]/@id'):
        love_node = str(love_node).replace('first', '')
        parent_node.append(love_node)
    space = ' ' * 2 * count
    for i in all_node:
        if i in parent_node:
            with open('code/code_tree.yml', 'a+', encoding='utf-8') as f:
                s = space[:-2] + '- ' + i + ':'
                f.write(s)
                f.write('\r\n')
            get_node(i, session, count + 1)
        else:
            with open('code/code_tree.yml', 'a+', encoding='utf-8') as f:
                s = space[:-2] + '- ' + i
                f.write(s)
                f.write('\r\n')


if __name__ == '__main__':
    for i in ['A', 'B', 'C', 'D', 'E', 'I']:
        with open('code/code_tree.yml', 'a+', encoding='utf-8') as f:
            f.write('I:')
            f.write('\r\n')
            get_node('I', session, 1)
