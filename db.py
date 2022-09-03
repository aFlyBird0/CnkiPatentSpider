from settings import mysql_connect

"""
数据库操作相关的内容都可以写在这个文件里
"""
if __name__ == '__main__':
    print('这里是 mysql 和如何在开源项目中保存敏感信息的示例。')
    # 简单来说，就是把敏感配置信息放在文件 A 中，
    # 并使用 gitignore 忽略文件 A，
    # 再提供一个内容结构和文件 A 一样的文件 A_example，
    # 供开发者重命名为 A 并填写自己的配置信息。
    print(mysql_connect)
